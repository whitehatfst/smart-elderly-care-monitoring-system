# 智慧养老监控系统

> 基于 Flask + OpenCV / dlib 的养老院智能看护系统：Web 管理后台 + 计算机视觉行为检测。
> A smart elderly-care monitoring system with a Flask admin dashboard and OpenCV-based behavior detection.

---

## 项目简介

本仓库是一套智慧养老监控系统的完整源码，按实训任务的推进顺序拆分为 **37 个任务目录**：

- **Web 端（15 个任务）**：Flask 管理后台，覆盖登录鉴权、系统管理员、老人、工作人员、义工、事件数据管理等功能模块。
- **计算机视觉（22 个任务）**：摄像头采集、人脸检测、表情识别、陌生人识别、摔倒检测、电子围栏、老人-义工互动检测等。

每个任务目录都是该阶段源码的**快照**，包含 `任务说明.txt`、`代码清单.txt`、`环境配置.txt`、`requirements.txt` 与 `代码/` 目录。单个任务目录不可独立运行，完整工程需要按 [组装完整工程](#2-组装完整工程) 合并。

---

## 功能概览

### Web 管理后台

| 模块 | 说明 |
| --- | --- |
| 登录鉴权 | 邮箱 + 密码登录，Flask-Login 会话管理，未登录跳转超时页 |
| 系统管理员 | 管理员信息列表与维护、密码修改 |
| 老人管理 | 信息增删改查、头像上传、性别 / 年龄段分布统计 |
| 工作人员管理 | 信息增删改查、头像管理、统计报表 |
| 义工管理 | 信息增删改查、头像管理、统计报表 |
| 事件管理 | 事件列表、实时报表（ECharts）、事件接收 API `/datamanage/api/insertevent` |

### 计算机视觉能力

| 能力 | 入口脚本 |
| --- | --- |
| 摄像头视频流服务 | `startingcameraservice.py` |
| 摄像头录像 | `startingrecording.py` |
| 人脸样本采集 | `collectingfaces.py` |
| 人脸识别模型训练 / 测试 | `trainingfacerecognition.py` / `testingfacerecognition.py` |
| 表情识别模型训练 / 测试 | `trainingfacialexpression.py` / `testingfacialexpression.py` |
| 摔倒检测模型训练 / 测试 | `trainingfalldetection.py` / `testingfalldetection.py` |
| 电子围栏（禁止区域入侵） | `checkingfence.py` |
| 摔倒检测并上报事件 | `checkingfalldetection.py` |
| 陌生人 + 表情联合检测 | `checkingstrangersandfacialexpression.py` |
| 老人-义工互动检测 | `checkingvolunteeractivity.py` |
| 人员变更后重建信息表 | `insertingnewpeople.py` |

---

## 技术栈

- **语言**：Python `3.10`
- **Web**：Flask `2.2.5`、Flask-Login、Flask-SQLAlchemy、Flask-SocketIO、eventlet
- **数据库**：SQLite（默认，开箱即用）/ MySQL（可选，见 `任务01A`）
- **计算机视觉**：OpenCV `4.10`、dlib、face_recognition、imutils
- **深度学习**：TensorFlow `2.10.1`、Keras `2.10.0`、scikit-learn
- **前端**：Jinja2 模板 + Bootstrap 风格页面 + ECharts 图表
- **依赖管理**：`pip` + `requirements.txt`

> 推荐在 Windows 10/11 下运行；不建议使用 Python 3.12+，部分旧依赖兼容性较差。

---

## 目录结构

```text
.
├── Web端/                                   # Web 后台，15 个任务
│   ├── 任务01_配置开发环境/
│   │   ├── 任务说明.txt                      # 本阶段做了什么
│   │   ├── 代码清单.txt                      # 源工程文件清单
│   │   ├── 环境配置.txt                      # 本阶段依赖
│   │   ├── requirements.txt
│   │   └── 代码/oldcaresystemweb/            # 源码快照
│   ├── 任务01A_ubuntu环境下安装配置mysql/
│   └── 任务02 ... 任务14/
├── 计算机视觉/                               # 视觉检测，22 个任务
│   ├── 任务01_图像采集-摄像头图像捕捉/
│   ├── ...
│   └── 任务22_计算机视觉代码整合/代码/old_care_system/
├── 总说明.txt
├── .gitignore
└── README.md
```

组装后的完整工程结构：

```text
old-care-system/
├── oldcaresystemweb/            # Web 后台
│   ├── runit.py                 # 启动入口
│   ├── config.py                # 配置文件
│   ├── old_care.sql             # 数据库导出脚本
│   ├── rebuild_sqlite_from_dump.py
│   ├── clouddata.db             # 首次启动自动生成的 SQLite 库
│   └── app/                     # 蓝图：auth / user / oldperson / employee / volunteer / eventinfo
└── old_care_system/             # 视觉检测
    ├── code/                    # 检测脚本
    ├── images/                  # 测试视频与人脸图片（仓库未分发）
    ├── models/                  # 已训练模型（仓库未分发）
    ├── info/                    # 人员与表情标签表
    ├── audios/                  # 告警音频（仓库未分发）
    └── supervision/             # 运行时截图与录像输出
```

---

## 任务清单

### Web 端（15 个任务）

| 编号 | 任务 | 内容 |
| --- | --- | --- |
| 01A | ubuntu 环境下安装配置 mysql | 数据库配置参考文件（当前仓库默认 SQLite） |
| 01 | 配置开发环境 | 启动入口、配置文件、初始化说明、数据库脚本 |
| 02 | 用户登录 | 登录鉴权、用户模型、登录页模板 |
| 03 | 系统管理员信息维护 | 管理员列表与表单维护 |
| 04 | 系统管理员密码修改 | 密码修改逻辑（含在用户模块内） |
| 05 | 老年人模块增删改查 | 老人信息维护模块与页面 |
| 06 | 老年人模块头像管理 | 老人头像上传与列表页 |
| 07 | 老年人模块报表统计 | 老人统计页面与图表依赖 |
| 08 | 工作人员模块增删改查 | 工作人员信息维护模块与页面 |
| 09 | 工作人员模块头像管理 | 工作人员头像页与头像数据 |
| 10 | 工作人员模块报表统计 | 工作人员统计页面与图表依赖 |
| 11 | 义工信息模块增删改查 | 义工信息维护模块与页面 |
| 12 | 义工模块头像管理 | 义工头像管理页面与后端模块 |
| 13 | 义工模块报表统计 | 义工统计页面与图表依赖 |
| 14 | 数据管理模块实时报表 | 事件管理、SocketIO 实时推送、报表页 |

### 计算机视觉（22 个任务）

| 编号 | 任务 | 内容 |
| --- | --- | --- |
| 01 | 图像采集-摄像头图像捕捉 | 摄像头服务、视频流模板、摄像头工具 |
| 02 | 图像采集-人脸检测-dlib | 基于 dlib / face_recognition 的人脸检测 |
| 03 | 图像采集-人脸检测-haar-cascade+adaboost | 未包含独立实现，仅保留任务说明 |
| 04 | 图像采集-人脸检测-MTCNN | 未包含独立实现，仅保留任务说明 |
| 05 | 图像采集-测试数据的收集 | 人脸样本提取代码与样本目录 |
| 06 | 图像采集-功能测试 | 主要视觉测试脚本汇总 |
| 07 | 图像采集-老人员工义工人脸图像采集 | 老人、工作人员采集样本 |
| 08 | 情感分析-业务数据的收集 | 表情识别样本与标签信息 |
| 09 | 情感分析-表情识别 | 表情识别训练、测试、联合检测 |
| 10 | 情感分析-测试数据收集 | 表情识别测试样本 |
| 11 | 情感分析-功能测试 | 表情识别测试与联动检测脚本 |
| 12 | 陌生人识别-识别陌生人 | 人脸识别模型 + 人员信息表 |
| 13 | 陌生人识别-测试数据收集 | 人员图片样本、采集脚本、人员信息表 |
| 14 | 陌生人识别-功能测试 | 人脸识别与陌生人判定验证 |
| 15 | 老人摔倒监测-业务数据收集 | 摔倒图片提取脚本与抓拍样本 |
| 16 | 老人摔倒监测-摔倒识别 | 摔倒识别训练、检测、测试 |
| 17 | 老人摔倒监测-测试数据收集 | 摔倒测试样本生成与样例抓拍 |
| 18 | 老人摔倒监测-功能测试 | 识别结果与事件上报验证 |
| 19 | 禁止区域入侵检测 | 电子围栏检测、目标检测模型 |
| 20 | 老人义工互动检测 | 义工互动检测、人脸工具、跟踪模块 |
| 21 | 摄像头画面实时显示（选做） | 浏览器视频流实时显示与录像 |
| 22 | 计算机视觉代码整合 | 全部视觉核心代码、信息文件、音频资源 |

---

## 快速开始

### 1. 环境要求

- Python `3.10`（64 位）
- Windows 10/11 或 Ubuntu 20.04+；需要摄像头、OpenCV 窗口显示时必须有图形界面
- 建议 8 GB 以上内存（TensorFlow 推理较吃内存）

### 2. 组装完整工程

任务目录是增量快照，请先合并成完整工程再运行。

**Windows（PowerShell）**

```powershell
# Web 端：按任务编号顺序覆盖合并，后一个任务包含前一个任务的改动
$dst = ".\build\oldcaresystemweb"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Get-ChildItem ".\Web端" -Directory |
    Where-Object { $_.Name -notlike "*01A*" } |
    Sort-Object Name |
    ForEach-Object {
        $src = Join-Path $_.FullName "代码\oldcaresystemweb"
        if (Test-Path $src) { Copy-Item "$src\*" $dst -Recurse -Force }
    }

# 计算机视觉：任务22 已是整合版，直接复制
Copy-Item ".\计算机视觉\任务22_计算机视觉代码整合\代码\old_care_system" ".\build\old_care_system" -Recurse -Force
```

**Linux / macOS（Bash）**

```bash
mkdir -p build/oldcaresystemweb
for d in Web端/任务0[1-9]* Web端/任务1[0-4]*; do
  case "$d" in *01A*) continue ;; esac
  cp -r "$d/代码/oldcaresystemweb/." build/oldcaresystemweb/ 2>/dev/null
done

cp -r "计算机视觉/任务22_计算机视觉代码整合/代码/old_care_system" build/old_care_system
```

> **合并后仍需补齐两个文件**：`oldcaresystemweb/app/views.py` 与 `oldcaresystemweb/app/templates/session_timeout.html`。
> 这两个文件在原工程中存在，但未被纳入任务快照：
>
> - `app/views.py`：所有路由都由 `app/mod_*/forms.py` 注册，该文件只需作为模块存在（可为空文件，加一行注释即可），供 `app/__init__.py` 的 `from app import views` 导入；
> - `app/templates/session_timeout.html`：未登录访问受保护页面时的提示页，内容可自定义。

### 3. 安装依赖

```powershell
cd .\build
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r ..\Web端\任务01_配置开发环境\requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

视觉脚本依赖较多，可用 `计算机视觉\任务22_计算机视觉代码整合\requirements.txt` 单独安装。

### 4. 启动 Web 后台

```powershell
cd .\build\oldcaresystemweb
python runit.py
```

- 登录页：<http://127.0.0.1:5000/>
- 数据管理页：<http://127.0.0.1:5000/datamanage>

首次启动会自动建表并创建默认管理员账号（**仅用于本地演示**）：

| 项目 | 值 |
| --- | --- |
| 登录邮箱 | `admin@example.com` |
| 登录密码 | `123abc` |

> 登录页实际校验的是**邮箱 + 密码**，不是用户名 + 密码。

### 5. 数据库初始化与重置

```powershell
# 方式一：首次启动自动建表 + 创建默认管理员
python runit.py

# 方式二：按 old_care.sql 导出内容重建（会先自动备份旧库）
python rebuild_sqlite_from_dump.py

# 方式三：删除数据库文件后重新启动，回到空库状态
Remove-Item .\clouddata.db
python runit.py
```

### 6. 运行视觉检测脚本

先确保 Web 后台已启动（脚本会把事件 POST 到 `http://127.0.0.1:5000/datamanage/api/insertevent`），再执行：

```powershell
cd .\build\old_care_system\code

# 电子围栏
python checkingfence.py --filename ..\images\tests\videos\yard_01.mp4

# 表情识别
python testingfacialexpression.py --filename ..\images\tests\videos\room_01.mp4

# 义工互动
python testingvolunteeractivity.py --filename ..\images\tests\videos\desk_01.mp4

# 摔倒检测（写入后台）
python checkingfalldetection.py --filename ..\images\tests\videos\corridor_01.avi

# 陌生人与表情联合检测
python checkingstrangersandfacialexpression.py --filename ..\images\tests\videos\room_01.mp4
```

去掉 `--filename` 参数即切换为本机摄像头实时检测（默认摄像头 `0`，多数窗口可按 `Esc` 退出）。

### 7. 摄像头服务与录像

```powershell
cd .\build\old_care_system\code

# 启动视频流服务，访问 http://127.0.0.1:5001/
python startingcameraservice.py --location room     # room / yard / corridor / desk

# 录像，输出到 old_care_system\supervision\records
python startingrecording.py --location room
```

---

## 资源文件说明

为保证仓库体积可控、避免肖像权问题，以下资源**未随仓库分发**，需要自行准备：

| 资源 | 路径 | 获取方式 |
| --- | --- | --- |
| 人脸识别模型 | `old_care_system/models/face_recognition_hog.pickle` | `python trainingfacerecognition.py` 训练生成 |
| 表情识别模型 | `old_care_system/models/face_expression.hdf5` | `python trainingfacialexpression.py` 训练生成 |
| 摔倒检测模型 | `old_care_system/models/fall_detection.hdf5` | `python trainingfalldetection.py` 训练生成 |
| 目标检测模型 | `old_care_system/models/mobilenet_ssd/` | 自行下载 MobileNet-SSD 权重 |
| 测试视频 | `old_care_system/images/tests/videos/` | 自备 mp4 / avi 素材 |
| 人脸样本 | `old_care_system/images/faces/` | `python collectingfaces.py --id <编号> --imagedir <目录>` 采集 |
| 告警音频 | `old_care_system/audios/` | 自备提示音文件 |

训练脚本运行前需要先准备好对应的人脸 / 摔倒样本图片，并按脚本内的目录约定存放。

---

## 配置项

`oldcaresystemweb/config.py` 中的敏感配置已改为从环境变量读取：

| 环境变量 | 作用 | 默认值 |
| --- | --- | --- |
| `SECRET_KEY` | Flask 会话签名密钥 | `dev-secret-key-please-change` |
| `CSRF_SESSION_KEY` | CSRF 签名密钥 | `dev-csrf-key-please-change` |
| `DEFAULT_ADMIN_PASSWORD` | 首次启动创建的默认管理员密码 | `123abc` |

```powershell
$env:SECRET_KEY = "<随机字符串>"
$env:DEFAULT_ADMIN_PASSWORD = "<强密码>"
python runit.py
```

其他可调项：`config.py` 中 `SQLALCHEMY_DATABASE_URI`（默认 SQLite，可改为 MySQL 连接串）。

---

## 数据与隐私说明

本仓库在发布前已做脱敏处理：

- **移除个人身份信息**：不含学号、姓名、指导教师、评阅表等个人标识信息，也不含任何真实人员的照片、视频与录音。
- **示例数据脱敏**：数据库种子数据中的人名统一替换为 `示例老人01` ~ `示例老人04`、`义工甲`、`义工乙`；身份证号与手机号统一替换为全 `0` 占位。
- **路径通用化**：源码与 SQL 中的开发者本机目录（Linux 用户主目录、Windows 盘符路径）统一替换为通用部署路径 `/opt/oldcare/...` 或仓库相对路径。
- **密钥外置**：会话密钥不再硬编码，改为环境变量注入。

仓库中的账号、密码、人员数据均为演示占位值，与任何真实个人无关。

---

## 已知限制

- 任务目录是**阶段性快照**，单独一个目录无法运行，必须先合并。
- 合并后仍缺少 `app/views.py`、`app/templates/session_timeout.html` 两个胶水文件（原工程存在，未纳入快照），需按 [组装完整工程](#2-组装完整工程) 的提示补齐。
- Web 端为教学演示工程：默认 `DEBUG=True`、密码使用 MD5 存储、无 CSRF 表单令牌、无权限分级校验。**请勿直接用于生产环境。**
- 摄像头视频服务监听 `0.0.0.0:5001`，仅建议在受信网络内使用。
- 部分视觉脚本依赖固定端口与本地地址，跨机部署时需同步修改上报地址。

---

## 常见问题

**1. TensorFlow 提示 `cudart64_110.dll` 缺失**
TensorFlow 2.10 在无 GPU 环境下的常见提示，通常不影响 CPU 模式运行。

**2. `dlib` / `face_recognition` 安装失败**
需先安装 CMake 与 Visual Studio Build Tools（C++ 生成工具），并保持 `setuptools<81`；建议直接使用仓库内整理好的 `requirements.txt` 配合国内镜像。

**3. 事件没有写入后台**
优先使用 `checkingfence.py`、`testingfacialexpression.py`、`testingvolunteeractivity.py` 等较新的脚本；若返回 500，检查 POST 到 `/datamanage/api/insertevent` 的 JSON 字段是否完整。

**4. OpenCV 窗口不弹出或摄像头打不开**
确认运行环境有桌面图形界面、Windows 摄像头权限已允许 Python 访问、且摄像头未被其他程序占用。

**5. 登录后页面空白 / 报模块缺失**
说明工程未合并完整，`app/` 下缺少后续任务的模块，请重新执行「组装完整工程」步骤。

---

## 贡献

欢迎提交 Issue 与 Pull Request。修改代码前请确认：

- 不提交任何真实人员数据、照片、视频；
- 不提交本地数据库文件（`*.db`）、模型权重与大体积媒体文件；
- 不硬编码密钥、密码与个人路径。

---

## 免责声明

本项目仅用于学习与技术交流，不得用于真实养老机构的实际监护场景。如需落地使用，请自行完成安全加固、隐私合规评估与相关资质备案。
