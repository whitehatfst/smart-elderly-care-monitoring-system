#开一个虚拟环境， python3.8

pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

#fence events
cd ..\old_care_system\code
python checkingfence.py --filename ..\images\tests\videos\yard_01.mp4
