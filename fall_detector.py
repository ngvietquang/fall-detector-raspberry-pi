# detector.py
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
import time
from send_mail import EmailSender
import threading
class FallDetector:
    def __init__(self, tflite_path, yolo_path, frame_count=8):
        # Load TFLite
        self.interpreter = tf.lite.Interpreter(model_path=tflite_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.pose_model = YOLO(yolo_path)

        self.sequence = []
        self.FRAME_COUNT = frame_count
        
        self.last_label = "NORMAL"
        self.last_prob = 0.0

        self.fall_start_time = None
        self.last_email_time = 0
        self.dismissed = False
        self.email_sender = EmailSender()
    def process_frame(self, frame, frame_id):


        # Chỉ xử lý mỗi 2 frame
        if frame_id % 2 != 0:
            return frame
        frame_small = cv2.resize(frame, (192, 192))
        results = self.pose_model.predict(frame_small, imgsz=192, conf=0.2, verbose=False)
            
        # vẽ bounding box và nhãn nếu có người được phát hiện
        if len(results[0].boxes) == 0:
            self.last_label = "NORMAL"
            self.last_prob = 0.0
        # Trong hàm process_frame
        if len(results[0].boxes) > 0:
            h_orig, w_orig = frame.shape[:2]
            # Lấy thông tin box đầu tiên
            box = results[0].boxes.xyxy[0].cpu().numpy() 
            x1, y1, x2, y2 = box
            # Lấy kích thước ảnh 
            img_h_yolo, img_w_yolo = results[0].orig_shape 

            # Tính toán tỉ lệ scale chính xác
            scale_x = w_orig / img_w_yolo
            scale_y = h_orig / img_h_yolo

            # Chuyển đổi tọa độ về ảnh gốc
            ix1 = int(x1 * scale_x)
            iy1 = int(y1 * scale_y)
            ix2 = int(x2 * scale_x)
            iy2 = int(y2 * scale_y)
            
            # Vẽ lên khung hình gốc
            cv2.rectangle(frame, (ix1, iy1), (ix2, iy2), (0, 0, 255), 2)
            cv2.putText(frame, "Person", (ix1, iy1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        if len(results[0].keypoints) > 0:
            keypoints = results[0].keypoints.xy[0].cpu().numpy().flatten()

            self.sequence.append(keypoints)

            if len(self.sequence) > self.FRAME_COUNT:
                self.sequence.pop(0)

            if len(self.sequence) == self.FRAME_COUNT:
                input_data = np.array(self.sequence, dtype=np.float32)
                input_data = input_data.reshape(1, self.FRAME_COUNT, 34)

                self.interpreter.set_tensor(
                    self.input_details[0]['index'], input_data
                )
                self.interpreter.invoke()

                output = self.interpreter.get_tensor(
                    self.output_details[0]['index']
                )

                prob = float(output[0][0])
                self.last_prob = prob
                if prob > 0.98:
                    self.last_label = "FALL"
                    if self.fall_start_time is None:
                        self.fall_start_time = time.time()
                        self.captured_frame = None 

                    elapsed = time.time() - self.fall_start_time
                    print(f"Đã ngã được: {elapsed:.1f}s")

                    if 2.0 <= elapsed <= 2.5 and self.captured_frame is None:
                        self.captured_frame = frame.copy() 
                        print("Đã chụp ảnh bằng chứng ở giây thứ 2")

        
                    if elapsed >= 10.0: #Sau 10 giây mà vẫn ngã thì gửi mail
                        current_time = time.time()
                        if not self.dismissed: #Nếu chưa dismiss thì mới gửi mail
                            frame_to_send = self.captured_frame if self.captured_frame is not None else frame
                            
                            cv2.imwrite("fall_evidence.png", frame_to_send)
                            print("Đủ 10 giây thì gửi mail cảnh báo ngã!")
                            
                            self.last_email_time = current_time
                            
                            email_thread = threading.Thread(
                                target=self.email_sender.send_email, 
                                args=("fall_evidence.png",),
                                daemon=True
                            )
                            email_thread.start()
                            

                else:
                    self.last_label = "NORMAL"
                    self.fall_start_time = None
                    self.captured_frame = None 
                    if self.dismissed:
                        self.dismissed = False

        return frame

    def draw_label(self, frame):
        color = (0, 0, 255) if self.last_label == "FALL" else (0, 255, 0)

        cv2.putText(
            frame,
            f"{self.last_label} {self.last_prob:.2f}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

        return frame
