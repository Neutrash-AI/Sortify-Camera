import cv2

def initialize_camera():
    """Inisialisasi kamera ArduCam IMX219 dan mengatur resolusi."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("Kamera gagal dibuka.")
        exit(1)
    return cap