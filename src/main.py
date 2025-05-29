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
import json
import serial

from tensorflow.keras.models import load_model

from camera import initialize_camera

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

# Konfigurasi Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL_NAME = "camera_frames"

MODEL_PATH = "./model/sortify_ai.h5"
USE_MODEL = os.path.exists(MODEL_PATH)  # True jika file model.h5 ada

model = None
if USE_MODEL:
    if os.path.isdir(MODEL_PATH):
        # format SavedModel (folder)
        model = load_model(MODEL_PATH)
    else:
        # format file (.h5 atau .keras single file)
        model = load_model(MODEL_PATH, compile=False)
else:
    print("Tidak ada model AI -> Mengirim raw video saja.")

# Inisialisasi Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

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


def run_inference(model, frame):
    """
    Melakukan inferensi menggunakan model klasifikasi sederhana berbasis CNN.
    Mengembalikan satu bounding box di tengah frame sebagai contoh.
    """
    input_frame = cv2.resize(frame, (150, 150))
    input_frame = input_frame.astype("float32") / 255.0
    input_frame = np.expand_dims(input_frame, axis=0)

    preds = model.predict(input_frame)
    class_id = np.argmax(preds[0])
    confidence = float(preds[0][class_id])

    # Map class_id to labels - 0:Organic, 1:Recycle
    labels = ["Organic", "Recycle"]
    # Ensure we don't get IndexError if model predicts unexpected class_id
    label = labels[class_id] if 0 <= class_id < len(labels) else "Unknown"

    h, w, _ = frame.shape
    # Make bounding box 3/4 of the smaller dimension (height or width)
    box_size = int(min(h, w) * 0.75)
    # Center the box in the frame
    x = w // 2 - box_size // 2
    y = h // 2 - box_size // 2
    bbox = [x, y, box_size, box_size]  # x, y, w, h

    return [{
        "label": label,
        "confidence": confidence,
        "bbox": bbox
    }]


def draw_bounding_box(frame, x, y, w, h, label, confidence):
    color = (0, 255, 0)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    text = f"{label} ({confidence:.2f})"
    cv2.putText(frame, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def main():
    """Fungsi utama untuk menangkap video, memprosesnya, dan mengirim hasil ke backend."""
    cap = initialize_camera()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            detections = []
            if USE_MODEL and model is not None:
                detections = run_inference(model, frame)
                for obj in detections:
                    x, y, w, h = obj["bbox"]
                    draw_bounding_box(frame, x, y, w, h,
                                      obj["label"], obj["confidence"])

                    send_serial_command(obj['label'])

            _, buffer = cv2.imencode(".jpg", frame)
            b64_frame = base64.b64encode(buffer).decode("utf-8")

            payload = {
                "hasModel": USE_MODEL,
                "timestamp": time.time(),
                "image": b64_frame,
                "detections": detections,
                "label": obj["label"] if detections else None,
            }

            r.publish(CHANNEL_NAME, json.dumps(payload))

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
    finally:
        cap.release()


if __name__ == "__main__":
    main()
