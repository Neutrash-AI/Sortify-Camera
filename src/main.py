"""
Script ini digunakan untuk streaming video dari kamera ArduCam IMX219 di Raspberry Pi.
Jika tersedia model AI, maka gambar akan diproses dan diberi bounding box sebelum dikirim.
Jika model AI tidak tersedia, gambar dikirim langsung ke backend melalui Redis.
"""

import os
import cv2
import time
import base64
import redis
import numpy as np

# from tensorflow.keras.models import load_model

from camera import initialize_camera

# Konfigurasi Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL_NAME = "camera_frames"

MODEL_PATH = "model.h5"
USE_MODEL = os.path.isfile(MODEL_PATH)  # True jika file model.h5 ada

model = None
if USE_MODEL:
    print(f"Model AI ditemukan -> {MODEL_PATH}")
    # model = load_model(MODEL_PATH)
else:
    print("Tidak ada model AI -> Mengirim raw video saja.")

# Inisialisasi Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def main():
    """Fungsi utama untuk menangkap video, memprosesnya, dan mengirim hasil ke backend."""
    cap = initialize_camera()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # if USE_MODEL and model is not None:
            #     detection_results = run_inference(model, frame)
            #     for obj in detection_results:
            #         label = obj["label"]
            #         confidence = obj["confidence"]
            #         x, y, w, h = obj["bbox"]
            #         draw_bounding_box(frame, x, y, w, h, label, confidence)

            _, buffer = cv2.imencode(".jpg", frame)
            b64_frame = base64.b64encode(buffer).decode("utf-8")

            payload = {
                # "hasModel": USE_MODEL,
                "timestamp": time.time(),
                "image": b64_frame,
            }
            
            r.publish(CHANNEL_NAME, str(payload))
            
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
    finally:
        cap.release()

if __name__ == "__main__":
    main()

