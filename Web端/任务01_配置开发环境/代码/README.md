# oldcaresystemweb（配置快照）

本目录是 `任务01_配置开发环境` 的源码快照，只包含工程启动所需的配置骨架：

| 文件 | 说明 |
| --- | --- |
| `runit.py` | Web 启动入口，负责建表、创建默认管理员并启动服务 |
| `config.py` | 应用配置（数据库、会话密钥等） |
| `app/__init__.py` | Flask 应用、SQLAlchemy、SocketIO、LoginManager 初始化 |
| `old_care.sql` | 数据库导出脚本（MySQL dump） |
| `rebuild_sqlite_from_dump.py` | 依据 `old_care.sql` 重建 SQLite 数据库 |
| `readme.txt` | 原始工程的简版运行说明 |

注意：本目录**不能单独运行**。`app/__init__.py` 会导入后续任务（`mod_user`、`mod_oldperson`、`mod_employee`、`mod_volunteer`、`mod_eventinfo`、`views`）中的模块，需要先按仓库根目录 `README.md` 的「组装完整工程」步骤合并，或直接把本目录视为完整工程的 `oldcaresystemweb` 根目录。

完整的安装、启动、数据库初始化与视觉脚本说明见仓库根目录的 [README.md](../../../README.md)。
