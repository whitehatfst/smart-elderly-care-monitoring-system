# -*- coding: utf-8 -*-
'''
义工是否和老人有互动主程序

用法： 
python testingvolunteeractivity.py
python testingvolunteeractivity.py --filename tests/desk_01.mp4
'''

from oldcare.facial import FaceUtil
from scipy.spatial import distance as dist
from oldcare.utils import fileassistant
from PIL import Image, ImageDraw, ImageFont
import cv2
import time
import imutils
import numpy as np
import argparse
import json
import urllib.request
from pathlib import Path
from runtime_paths import INFO_DIR, MODELS_DIR, get_font


# 传入参数
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=False, default = '',
	help="")
args = vars(ap.parse_args())

# 全局变量
pixel_per_metric = None
input_video = args['filename']
model_path = str(MODELS_DIR / 'face_recognition_hog.pickle')
people_info_path = str(INFO_DIR / 'people_info.csv')


def _debug_report(hypothesis_id: str, location: str, msg: str, data=None) -> None:
    # #region debug-point shared:testingvolunteeractivity
    _env_path = Path(__file__).resolve().parents[2] / ".dbg" / "volunteer-video-flash.env"
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

# 全局常量
FACE_ACTUAL_WIDTH = 20 # 单位厘米   姑且认为所有人的脸都是相同大小
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
ACTUAL_DISTANCE_LIMIT = 100# cm
REPORT_INTERVAL_SECONDS = 5

# 得到 ID->姓名的map 、 ID->职位类型的map
id_card_to_name, id_card_to_type = fileassistant.get_people_info(people_info_path)

# 初始化摄像头
if not input_video:
	vs = cv2.VideoCapture(0)
	time.sleep(2)
else:
	vs = cv2.VideoCapture(input_video)

# #region debug-point B:video-capture-created
_debug_report(
    "B",
    "testingvolunteeractivity.py:89",
    "[DEBUG] video capture created",
    {"input_video": input_video, "capture_opened": bool(vs.isOpened())},
)
# #endregion

if input_video and not vs.isOpened():
    # #region debug-point B:video-open-failed
    _debug_report(
        "B",
        "testingvolunteeractivity.py:98",
        "[DEBUG] video capture open failed",
        {"input_video": input_video},
    )
    # #endregion
    raise ValueError('无法打开视频文件: %s' % input_video)

# 加载模型
faceutil = FaceUtil(model_path)
    
print('[INFO] 开始检测义工和老人是否有互动...')
# #region debug-point A:script-started
_debug_report(
    "A",
    "testingvolunteeractivity.py:107",
    "[DEBUG] volunteer activity script started",
    {"input_video": input_video, "model_path": model_path, "people_info_path": people_info_path},
)
# #endregion
# 不断循环
counter = 0
last_reported_at = {}
while True:
    counter += 1
    # grab the current frame
    (grabbed, frame) = vs.read()
    if counter == 1:
        # #region debug-point B:first-frame
        _debug_report(
            "B",
            "testingvolunteeractivity.py:121",
            "[DEBUG] first frame read attempted",
            {
                "grabbed": bool(grabbed),
                "frame_is_none": frame is None,
            },
        )
        # #endregion

	# if we are viewing a video and we did not grab a frame, then we
	# have reached the end of the video
    if input_video and not grabbed:
        break
    
    if not input_video:
        frame = cv2.flip(frame, 1)
        
    frame = imutils.resize(frame, 
                           width = VIDEO_WIDTH, 
                           height = VIDEO_HEIGHT)#压缩，为了加快识别速度
    
    face_location_list, names = faceutil.get_face_location_and_name(frame)
    
    people_type_list = list(set([id_card_to_type[i] for i in names]))
    
    volunteer_centroids = []
    old_people_centroids = []
    old_people_name = []
    
    # loop over the face bounding boxes
    for ((left, top, right, bottom), name) in zip(face_location_list, names): # 处理单个人
        
        person_type = id_card_to_type[name]
		# 将人脸框出来
        rectangle_color = (0, 0, 255)
        if person_type == 'old_people':
            rectangle_color = (0, 0, 128)
        elif person_type == 'employee':
            rectangle_color = (255, 0, 0)
        elif person_type == 'volunteer':
            rectangle_color = (0, 255, 0)
        else:
            pass
        cv2.rectangle(frame, (left, top), (right, bottom),
                      rectangle_color, 2)
        
        if 'volunteer' not in people_type_list: # 如果没有义工，直接跳出本次循环
            continue
        
        if person_type == 'volunteer': # 如果检测到有义工存在
            # 获得义工位置
            volunteer_face_center = (int((right + left)/2), 
                                     int((top + bottom)/2))
            volunteer_centroids.append(volunteer_face_center)
        
            cv2.circle(frame, 
                       (volunteer_face_center[0], volunteer_face_center[1]), 
                       8, (255, 0, 0), -1)
            
        elif person_type == 'old_people': # 如果没有发现义工
            old_people_face_center = (int((right + left)/2), 
                                      int((top + bottom)/2))
            old_people_centroids.append(old_people_face_center)
            old_people_name.append(name)
        
            cv2.circle(frame, 
                       (old_people_face_center[0], old_people_face_center[1]), 
                       4, (0, 255, 0), -1)
        else:
            pass
        
        # 人脸识别和表情识别都结束后，把表情和人名写上 (同时处理中文显示问题)
        img_PIL = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) 
        draw = ImageDraw.Draw(img_PIL)
        final_label = id_card_to_name[name]
        draw.text((left, top - 30), final_label, 
                  font=get_font(40),
                  fill=(255,0,0))
        # 转换回OpenCV格式
        frame = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)
        
    # 在义工和老人之间划线
    for i in volunteer_centroids:
        for j_index, j in enumerate(old_people_centroids):
            pixel_distance = dist.euclidean(i, j)
            face_pixel_width = sum([i[2] - i[0] for i in face_location_list])/len(face_location_list)
            pixel_per_metric = face_pixel_width/FACE_ACTUAL_WIDTH
            actual_distance = pixel_distance/pixel_per_metric
            
            if actual_distance < ACTUAL_DISTANCE_LIMIT:
                cv2.line(frame, (int(i[0]), int(i[1])), 
                         (int(j[0]), int(j[1])),(255, 0, 255), 2)
                label= 'distance: %dcm' %(actual_distance)
                cv2.putText(frame, label, (frame.shape[1] - 150, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                            (0, 0, 255), 2)
                old_person_id = int(old_people_name[j_index])
                old_person_name = id_card_to_name[old_people_name[j_index]]
                now = time.time()

                if now - last_reported_at.get(old_person_id, 0) >= REPORT_INTERVAL_SECONDS:
                    current_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                                 time.localtime(now))
                    event_desc = '%s正在与义工交互' % old_person_name
                    event_location = '房间桌子'
                    print('[EVENT] %s, %s, %s.' % (current_time, event_location, event_desc))

                    try:
                        import requests

                        payload = {'id': 0,
                                   'event_name': '义工交互事件',
                                   'event_desc': event_desc,
                                   'event_type': 1,  # 0=微笑之星，1=互动事件，2=是危险事件
                                   'event_date': current_time,
                                   'event_location': event_location,
                                   'oldperson_id': old_person_id}
                        requests.post(
                            'http://127.0.0.1:5000/datamanage/api/insertevent',
                            json=payload,
                            timeout=3,
                        )
                        last_reported_at[old_person_id] = now
                    except Exception as e:
                        print(e)
                    
    
    # show our detected faces along with smiling/not smiling labels
    cv2.imshow("Checking Volunteer's Activities", frame)
    
    # Press 'ESC' for exiting video
    k = cv2.waitKey(1) & 0xff 
    if k == 27:
        break
    
# cleanup the camera and close any open windows
vs.release()
cv2.destroyAllWindows()
