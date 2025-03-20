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

