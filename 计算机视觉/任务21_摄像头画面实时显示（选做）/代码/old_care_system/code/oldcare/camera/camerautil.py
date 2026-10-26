# -*- coding: utf-8 -*-

from pathlib import Path
import os
import threading
import time

import cv2


class RecordingThread(threading.Thread):
    def __init__(self, camera, save_video_path, fps=20.0):
        super().__init__(name="Video Recording Thread", daemon=True)
        self.camera = camera
        self.save_video_path = Path(save_video_path)
        self.fps = fps
        self.is_running = True
        self.out = None

    def _build_writer(self, frame):
        self.save_video_path.parent.mkdir(parents=True, exist_ok=True)
        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.out = cv2.VideoWriter(
            str(self.save_video_path), fourcc, self.fps, (width, height), True
        )
        if not self.out.isOpened():
            self.out = None
            raise RuntimeError("Unable to open video writer for recording.")

    def run(self):
        try:
            while self.is_running:
                ret, frame = self.camera.read_raw_frame()
                if not ret:
                    time.sleep(0.01)
                    continue
                if self.out is None:
                    self._build_writer(frame)
                self.out.write(frame)
        finally:
            if self.out is not None:
                self.out.release()

    def stop(self):
        self.is_running = False


class VideoCamera(object):
    def __init__(self, camera_index=0):
        backend = cv2.CAP_DSHOW if os.name == "nt" else 0
        self.cap = cv2.VideoCapture(camera_index, backend)
        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError("Unable to open camera.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self._lock = threading.Lock()
        self._last_frame = None
        self.is_record = False
        self.recordingThread = None

    def __del__(self):
        self.close()

    def close(self):
        self.stop_record()
        if getattr(self, "cap", None) is not None:
            self.cap.release()
            self.cap = None

    def read_raw_frame(self):
        if self.cap is None:
            return False, None

        with self._lock:
            ret, frame = self.cap.read()

        if not ret:
            return False, None

        frame = cv2.flip(frame, 1)
        self._last_frame = frame
        return True, frame

    def get_frame(self):
        ret, frame = self.read_raw_frame()
        if not ret:
            frame = self._last_frame
            if frame is None:
                return None

        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            return None
        return jpeg.tobytes()

    def start_record(self, save_video_path):
        if self.is_record and self.recordingThread is not None:
            if self.recordingThread.is_alive():
                return False
            self.recordingThread = None

        self.recordingThread = RecordingThread(self, save_video_path)
        self.recordingThread.start()
        self.is_record = True
        return True

    def stop_record(self):
        self.is_record = False
        if self.recordingThread is not None:
            self.recordingThread.stop()
            self.recordingThread.join(timeout=2.0)
            self.recordingThread = None
