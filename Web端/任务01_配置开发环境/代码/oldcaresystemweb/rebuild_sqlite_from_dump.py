from __future__ import annotations

import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


WEB_ROOT = Path(__file__).resolve().parent
DUMP_PATH = WEB_ROOT / "old_care.sql"
SQLITE_PATH = WEB_ROOT / "clouddata.db"

TABLES = [
    "employee_info",
    "event_info",
    "oldperson_info",
    "sys_user",
    "volunteer_info",
]


def extract_create_block(sql_text: str, table_name: str) -> str:
    pattern = rf"CREATE TABLE `{table_name}` \((.*?)\) ENGINE=.*?;"
    match = re.search(pattern, sql_text, re.S)
    if not match:
        raise ValueError(f"CREATE TABLE block not found for {table_name}")
    return match.group(1)


def extract_insert_statement(sql_text: str, table_name: str) -> str | None:
    pattern = rf"INSERT INTO `{table_name}` VALUES\s*(.*?);"
    match = re.search(pattern, sql_text, re.S)
    if not match:
        return None
    values_sql = match.group(1).strip()
    return f'INSERT INTO "{table_name}" VALUES {values_sql};'


def convert_column_definition(line: str) -> str:
    line = line.strip().rstrip(",")
    if not line:
        return ""

    if line.startswith("PRIMARY KEY"):
        return ""

    line = re.sub(r"\s+COMMENT\s+'[^']*'", "", line)
    line = line.replace("`", '"')

    auto_increment = "AUTO_INCREMENT" in line.upper()
    line = re.sub(r"\s+AUTO_INCREMENT", "", line, flags=re.I)

    column_match = re.match(r'^"([^"]+)"\s+(.*)$', line)
    if not column_match:
        return line

    column_name, remainder = column_match.groups()

    if auto_increment:
        return f'"{column_name}" INTEGER PRIMARY KEY AUTOINCREMENT'

    return f'"{column_name}" {remainder}'


def build_create_statement(sql_text: str, table_name: str) -> str:
    block = extract_create_block(sql_text, table_name)
    converted_lines = []

    for raw_line in block.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        converted = convert_column_definition(stripped)
        if converted:
            converted_lines.append(f"    {converted}")

    body = ",\n".join(converted_lines)
    return f'CREATE TABLE "{table_name}" (\n{body}\n);'


def backup_existing_db() -> Path | None:
    if not SQLITE_PATH.exists():
        return None

    backup_name = f"clouddata_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
    backup_path = WEB_ROOT / backup_name
    shutil.copy2(SQLITE_PATH, backup_path)
    return backup_path


def rebuild_sqlite() -> None:
    if not DUMP_PATH.exists():
        raise FileNotFoundError(f"MySQL dump not found: {DUMP_PATH}")

    sql_text = DUMP_PATH.read_text(encoding="utf-8")
    backup_path = backup_existing_db()

    temp_db_path = WEB_ROOT / "clouddata.tmp.db"
    if temp_db_path.exists():
        temp_db_path.unlink()

    connection = sqlite3.connect(temp_db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")

        for table_name in TABLES:
            create_sql = build_create_statement(sql_text, table_name)
            cursor.executescript(f'DROP TABLE IF EXISTS "{table_name}";\n{create_sql}')

            insert_sql = extract_insert_statement(sql_text, table_name)
            if insert_sql:
                cursor.executescript(insert_sql)

        connection.commit()
    finally:
        connection.close()

    temp_db_path.replace(SQLITE_PATH)

    print("SQLite rebuild completed.")
    if backup_path:
        print(f"Backup created: {backup_path}")
    print(f"Database path: {SQLITE_PATH}")


if __name__ == "__main__":
    rebuild_sqlite()
