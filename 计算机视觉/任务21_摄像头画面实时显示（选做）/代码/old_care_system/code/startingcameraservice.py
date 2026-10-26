# -*- coding: utf-8 -*-

"""
启动摄像头主程序

用法:
python startingcameraservice.py
python startingcameraservice.py --location room

启动后访问 http://127.0.0.1:5001/ 查看摄像头实时画面。
"""

import argparse
import atexit
import time

from flask import Flask, Response, jsonify, render_template, request

from oldcare.camera import VideoCamera


VALID_LOCATIONS = ["room", "yard", "corridor", "desk"]


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--location", required=False, default="room", help="")
args = vars(ap.parse_args())
location = args["location"]

if location not in VALID_LOCATIONS:
    raise ValueError("location must be one of room, yard, corridor or desk")

app = Flask(__name__)

video_camera = None
global_frame = None


def get_video_camera():
    global video_camera
    if video_camera is None:
        video_camera = VideoCamera()
    return video_camera


@atexit.register
def release_camera():
    global video_camera
    if video_camera is not None:
        video_camera.close()
        video_camera = None


@app.route("/")
def index():
    return render_template(
        location + "_camera.html",
        location=location,
        location_name={
            "room": "房间",
            "yard": "院子",
            "corridor": "走廊",
            "desk": "桌面",
        }[location],
    )


@app.route("/health")
def health():
    try:
        get_video_camera()
        return jsonify({"status": "ok", "location": location})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/record_status", methods=["POST"])
def record_status():
    try:
        camera = get_video_camera()
    except Exception as exc:
        return str(exc), 500

    status = request.form.get("status", "").lower()
    save_video_path = request.form.get("save_video_path")

    if status == "true":
        if not save_video_path:
            return "missing save_video_path", 400
        started = camera.start_record(save_video_path)
        return "start record" if started else "already recording"

    camera.stop_record()
    return "stop record"


def video_stream():
    global global_frame

    while True:
        try:
            frame = get_video_camera().get_frame()
        except Exception:
            frame = global_frame

        if frame is None:
            time.sleep(0.05)
            continue

        global_frame = frame
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Cache-Control: no-cache\r\n\r\n" + frame + b"\r\n"
        )


@app.route("/video_viewer")
def video_viewer():
    return Response(
        video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True, port=5001)
