# 源码目录说明

`oldcare` 是包，包含所有代码的辅助模块。

| 目录 / 文件 | 说明 |
| --- | --- |
| `oldcare/` | 辅助包：camera、facial、track、servo、utils、conv、preprocessing、datasets、callbacks、audio |
| `adafruit/` | 舵机依赖包 |
| `templates/` | 摄像头预览页面 |
| `readme.txt` | 本说明文件 |
| 其余 `.py` 文件 | 主程序 |

## 主程序

| 脚本 | 说明 |
| --- | --- |
| `collectingfaces.py` | 采集人脸数据 |
| `trainingfacerecognition.py` | 训练人脸识别模型 |
| `testingfacerecognition.py` | 测试人脸识别模型 |
| `trainingfacialexpression.py` | 训练表情识别模型 |
| `testingfacialexpression.py` | 测试表情识别模型 |
| `trainingfalldetection.py` | 训练摔倒检测模型 |
| `testingfalldetection.py` | 测试摔倒检测模型 |
| `startingcameraservice.py` | 开启摄像头视频流服务 |
| `startingrecording.py` | 摄像头录像 |
| `testingvolunteeractivity.py` | 测试义工与老人互动 |
| `checkingvolunteeractivity.py` | 义工与老人互动检测主程序 |
| `testingfence.py` | 测试禁止区域入侵检测 |
| `checkingfence.py` | 禁止区域入侵检测主程序 |
| `checkingfalldetection.py` | 摔倒检测主程序 |
| `checkingstrangersandfacialexpression.py` | 陌生人识别与表情识别主程序 |
| `inserting.py` | 向后台写入数据的主程序 |
| `insertingcontrol.py` | 控制是否允许写入数据库 |
| `allowinsertdatabase.txt` | 写入数据库的开关文件 |
| `insertingnewpeople.py` | 人员信息变化后重建信息表与识别模型 |

## 运行前需要准备

`models/`、`images/`、`audios/` 等资源目录未随仓库分发，需自行训练或准备，详见仓库根目录 `README.md` 的「资源文件说明」。
