from __future__ import annotations

import datetime as dt
import os
import hashlib
import shutil
import subprocess
import sys
import threading
from pathlib import Path
import json
import urllib.request


WEB_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = WEB_ROOT.parent
OLD_CARE_SYSTEM_ROOT = PROJECT_ROOT / "old_care_system"
OLD_CARE_CODE_DIR = OLD_CARE_SYSTEM_ROOT / "code"
OLD_CARE_IMAGES_DIR = OLD_CARE_SYSTEM_ROOT / "images"
TEST_VIDEOS_DIR = OLD_CARE_IMAGES_DIR / "tests" / "videos"
LEGACY_TEST_VIDEOS_DIR = OLD_CARE_SYSTEM_ROOT / "tests" / "videos"

COLLECT_FACES_SCRIPT = OLD_CARE_CODE_DIR / "collectingfaces.py"
OLD_PERSON_FACES_DIR = OLD_CARE_IMAGES_DIR / "faces" / "old_people"
EMPLOYEE_FACES_DIR = OLD_CARE_IMAGES_DIR / "faces" / "employees"
VOLUNTEER_FACES_DIR = OLD_CARE_IMAGES_DIR / "faces" / "volunteers"

SQLITE_DB_PATH = WEB_ROOT / "clouddata.db"
_ACTIVE_DETECTORS_LOCK = threading.Lock()
_ACTIVE_DETECTORS: dict[str, subprocess.Popen] = {}
_ACTIVE_FACE_COLLECTORS_LOCK = threading.Lock()
_ACTIVE_FACE_COLLECTORS: dict[str, subprocess.Popen] = {}


def _debug_report(hypothesis_id: str, location: str, msg: str, data=None) -> None:
    # #region debug-point shared:runtime-support
    _env_path = PROJECT_ROOT / ".dbg" / "volunteer-video-flash.env"
    _url = "http://127.0.0.1:7777/event"
    _session = "volunteer-video-flash"
    try:
        if _env_path.exists():
            _content = _env_path.read_text(encoding="utf-8")
            for _line in _content.splitlines():
                if _line.startswith("DEBUG_SERVER_URL="):
                    _url = _line.split("=", 1)[1].strip()
                elif _line.startswith("DEBUG_SESSION_ID="):
                    _session = _line.split("=", 1)[1].strip()
        _payload = {
            "sessionId": _session,
            "runId": "pre-fix",
            "hypothesisId": hypothesis_id,
            "location": location,
            "msg": msg,
            "data": data or {},
        }
        urllib.request.urlopen(
            urllib.request.Request(
                _url,
                data=json.dumps(_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            ),
            timeout=1,
        ).read()
    except Exception:
        pass
    # #endregion


def ensure_directory(path: Path | str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def parse_datetime(value):
    if value in (None, "", "None"):
        return None
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.min)

    value = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = dt.datetime.strptime(value, fmt)
            if fmt == "%Y-%m-%d":
                return dt.datetime.combine(parsed.date(), dt.time.min)
            return parsed
        except ValueError:
            continue
    raise ValueError("Unsupported datetime format: %s" % value)


def md5_text(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def run_collect_faces(person_id: int, image_dir: Path | str) -> None:
    ensure_directory(image_dir)
    subprocess.run(
        [
            sys.executable,
            str(COLLECT_FACES_SCRIPT),
            "--id",
            str(person_id),
            "--imagedir",
            str(Path(image_dir)),
        ],
        cwd=str(OLD_CARE_CODE_DIR),
        check=False,
    )


def start_collect_faces(person_id: int, image_dir: Path | str) -> subprocess.Popen:
    ensure_directory(image_dir)
    collector_key = f"{Path(image_dir).resolve()}::{person_id}"

    with _ACTIVE_FACE_COLLECTORS_LOCK:
        active_process = _ACTIVE_FACE_COLLECTORS.get(collector_key)
        if active_process and active_process.poll() is None:
            return active_process

    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

    process = subprocess.Popen(
        [
            sys.executable,
            str(COLLECT_FACES_SCRIPT),
            "--id",
            str(person_id),
            "--imagedir",
            str(Path(image_dir)),
        ],
        cwd=str(OLD_CARE_CODE_DIR),
        creationflags=creationflags,
    )
    with _ACTIVE_FACE_COLLECTORS_LOCK:
        _ACTIVE_FACE_COLLECTORS[collector_key] = process

    def _watch_process() -> None:
        process.wait()
        with _ACTIVE_FACE_COLLECTORS_LOCK:
            if _ACTIVE_FACE_COLLECTORS.get(collector_key) is process:
                _ACTIVE_FACE_COLLECTORS.pop(collector_key, None)

    threading.Thread(target=_watch_process, daemon=True).start()
    return process


def sync_person_images(source_dir: Path | str, target_root: Path | str) -> None:
    source = Path(source_dir)
    target_root = ensure_directory(target_root)
    if not source.exists():
        return

    target_dir = target_root / source.name
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source, target_dir)


def resolve_test_video(video_name: str) -> Path:
    primary_path = TEST_VIDEOS_DIR / video_name
    if primary_path.exists():
        return primary_path

    legacy_path = LEGACY_TEST_VIDEOS_DIR / video_name
    if legacy_path.exists():
        return legacy_path

    return primary_path


def run_detector(script_name: str, video_name: str) -> subprocess.Popen:
    script_path = OLD_CARE_CODE_DIR / script_name
    video_path = resolve_test_video(video_name)
    # #region debug-point D:detector-inputs
    _debug_report(
        "D",
        "runtime_support.run_detector:102",
        "[DEBUG] run_detector called",
        {
            "script_name": script_name,
            "video_name": video_name,
            "script_path": str(script_path),
            "video_path": str(video_path),
            "cwd": str(OLD_CARE_CODE_DIR),
            "python": sys.executable,
        },
    )
    # #endregion

    if not script_path.exists():
        # #region debug-point D:missing-script
        _debug_report("D", "runtime_support.run_detector:116", "[DEBUG] detector script missing", {"script_path": str(script_path)})
        # #endregion
        raise FileNotFoundError(f"Detector script not found: {script_path}")
    if not video_path.exists():
        # #region debug-point B:missing-video
        _debug_report("B", "runtime_support.run_detector:120", "[DEBUG] detector video missing", {"video_path": str(video_path)})
        # #endregion
        raise FileNotFoundError(f"Detector video not found: {video_path}")

    with _ACTIVE_DETECTORS_LOCK:
        active_process = _ACTIVE_DETECTORS.get(script_name)
        if active_process and active_process.poll() is None:
            # #region debug-point C:process-already-running
            _debug_report(
                "C",
                "runtime_support.run_detector:128",
                "[DEBUG] detector already running, skip duplicate launch",
                {"script_name": script_name, "pid": active_process.pid},
            )
            # #endregion
            return active_process

    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

    process = subprocess.Popen(
        [sys.executable, str(script_path), "--filename", str(video_path)],
        cwd=str(OLD_CARE_CODE_DIR),
        creationflags=creationflags,
    )
    with _ACTIVE_DETECTORS_LOCK:
        _ACTIVE_DETECTORS[script_name] = process
    # #region debug-point A:process-created
    _debug_report(
        "A",
        "runtime_support.run_detector:131",
        "[DEBUG] detector process created",
        {"pid": process.pid, "creationflags": creationflags},
    )
    # #endregion

    # #region debug-point A:process-exit-watch
    def _watch_process() -> None:
        exit_code = process.wait()
        with _ACTIVE_DETECTORS_LOCK:
            if _ACTIVE_DETECTORS.get(script_name) is process:
                _ACTIVE_DETECTORS.pop(script_name, None)
        _debug_report(
            "A",
            "runtime_support.run_detector:141",
            "[DEBUG] detector process exited",
            {"pid": process.pid, "exit_code": exit_code},
        )

    threading.Thread(target=_watch_process, daemon=True).start()
    # #endregion
    return process
