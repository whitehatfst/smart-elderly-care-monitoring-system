# -*- coding: utf-8 -*-

"""
录像
按 Ctrl+C 结束录像

用法：
python startingrecording.py
python startingrecording.py --location room
"""

import argparse
import time
from pathlib import Path

import requests

from runtime_paths import SUPERVISION_DIR, ensure_directory


VALID_LOCATIONS = ["room", "yard", "corridor", "desk"]


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--location", required=False, default="room", help="")
args = vars(ap.parse_args())
location = args["location"]

if location not in VALID_LOCATIONS:
    raise ValueError("location must be one of room, yard, corridor or desk")


camera_host_ip = "127.0.0.1"
camera_host_port = 5001
records_dir = ensure_directory(SUPERVISION_DIR / "records")
timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))
save_video_path = Path(records_dir) / f"{location}_{timestamp}.avi"
base_url = f"http://{camera_host_ip}:{camera_host_port}"


def post_record_status(status, save_path=None):
    payload = {"status": status}
    if save_path is not None:
        payload["save_video_path"] = str(save_path)
    response = requests.post(f"{base_url}/record_status", data=payload, timeout=10)
    response.raise_for_status()
    return response.text.strip()


out = post_record_status("true", save_video_path)
if out == "start record":
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print("[INFO] %s 录像程序启动了，文件保存到 %s." % (current_time, save_video_path))
else:
    raise ValueError("[ERROR] 录像程序出现问题: %s" % out)

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    pass


out = post_record_status("false")
if out == "stop record":
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print("[INFO] %s 停止录像程序启动了." % current_time)
else:
    raise ValueError("[ERROR] 停止录像程序出现问题: %s" % out)


