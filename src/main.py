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

# Konfigurasi Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL_NAME = "camera_frames"

# Inisialisasi Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

