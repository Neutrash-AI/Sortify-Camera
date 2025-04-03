import cv2
import sys

def initialize_camera():
    """
    Inisialisasi kamera berdasarkan mode.
    Jika parameter 'prod' ada pada command line, maka menggunakan GStreamer pipeline untuk kamera ArduCam.
    Jika tidak, menggunakan kamera webcam biasa.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "prod":
        print("Menggunakan kamera ArduCam dengan GStreamer pipeline.")
        # GStreamer pipeline untuk ArduCam IMX219
        gst_pipeline = (
            "libcamerasrc ! video/x-raw,width=640,height=480,format=NV12 "
            "! videoconvert ! appsink"
        )
        cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    else:
        print("Menggunakan kamera webcam biasa.")
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Kamera gagal dibuka.")
        exit(1)
    return cap
