
from camera import CameraStream
from fall_detector import FallDetector
from app import WebApp



camera = CameraStream(0)

# Khởi tạo bộ phát hiện té ngã
detector = FallDetector(
    tflite_path="fall_model_pi_3.tflite",
    yolo_path="yolov8n-pose_19x.onnx",
    frame_count=8
)

web = WebApp(camera, detector)

web.run()
