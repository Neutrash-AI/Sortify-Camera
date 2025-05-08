"""
Script ini digunakan untuk streaming video dari ESP32-S3 (OV2640) via serial dan integrasi AI.
Perintah kamera diakhiri dengan karakter '\n'.
Python membaca header 4 byte (panjang frame), lalu frame JPEG, proses inferensi, gambar bounding box, kirim perintah ke ESP, dan kirim payload via Redis.
"""

import os
import time
import base64
import redis
import json
import struct

import cv2
import numpy as np
from tensorflow.keras.models import load_model
import serial

# Konfigurasi serial ke ESP32
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Konfigurasi Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL_NAME = "camera_frames"

# Model AI
MODEL_PATH = "./model/sortify_ai.h5"
USE_MODEL = os.path.exists(MODEL_PATH)
model = None
if USE_MODEL:
    print(f"Model AI ditemukan -> {MODEL_PATH}")
    # load_model dengan compile=False untuk struktur h5
    model = load_model(MODEL_PATH, compile=False)
else:
    print("Tidak ada model AI -> Mengirim raw video saja.")

# Redis client
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

# Fungsi inferensi dan bounding box
def run_inference(model, frame):
    # Resize sesuai input model
    img = cv2.resize(frame, (150,150)).astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)
    preds = model.predict(img)
    class_id = np.argmax(preds[0])
    confidence = float(preds[0][class_id])
    labels = ["Organic","Recycle"] # index 0=Organic,1=Recycle
    label = labels[class_id] if 0<=class_id<len(labels) else "Unknown"
    h,w,_ = frame.shape
    size = int(min(h,w)*0.75)
    x = w//2 - size//2
    y = h//2 - size//2
    return [{"label":label,"confidence":confidence,"bbox":[x,y,size,size]}]

# Gambar box pada frame
def draw_bounding_box(frame,obj):
    x,y,w,h = obj['bbox']
    color=(0,255,0)
    cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
    text=f"{obj['label']} ({obj['confidence']*100:.1f}%)"
    cv2.putText(frame,text,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,color,2)

# Kirim perintah ke ESP32 berdasarkan label deteksi
def send_serial_command(label):
    # Sesuaikan perintah: 'S 0' untuk Recycle, 'S 1' untuk Organic
    cmd = None
    if label == 'Recycle':
        cmd = 'S 0'
    elif label == 'Organic':
        cmd = 'S 1'
    if cmd:
        ser.write((cmd + '\n').encode('utf-8'))
        print(f"Sent command to ESP: {cmd}")

# Proses utama
while True:
    # Baca header 4 byte little-endian
    hdr = ser.read(4)
    if len(hdr)<4:
        continue
    length = struct.unpack('<I',hdr)[0]
    # Baca data JPEG sesuai header
    data = bytearray()
    while len(data)<length:
        packet = ser.read(length - len(data))
        if not packet:
            break
        data.extend(packet)
    if len(data)!=length:
        continue  # skip frame jika incomplete

    # Decode JPEG frame
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        continue

    detections=[]
    if USE_MODEL and model is not None:
        detections = run_inference(model, frame)
        for obj in detections:
            draw_bounding_box(frame,obj)
            # Kirim perintah ke ESP berdasarkan label
            send_serial_command(obj['label'])

    # Encode ke base64
    _,buf = cv2.imencode('.jpg',frame)
    b64 = base64.b64encode(buf).decode('utf-8')

    payload={
        'hasModel':USE_MODEL,
        'timestamp':time.time(),
        'image':b64,
        'detections':detections
    }
    # Kirim dengan newline sebagai penanda akhir
    msg = json.dumps(payload) + '\n'
    r.publish(CHANNEL_NAME, msg)

    # Optional: delay sesuai fps target
    time.sleep(0.1)  # ~10 fps
