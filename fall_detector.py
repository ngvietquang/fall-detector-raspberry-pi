# detector.py
import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
import time
<<<<<<< HEAD
from send_mail import EmailSender  # Đảm bảo file đặt tên đúng
import threading
import os

=======
from send_mail import EmailSender
import threading
>>>>>>> aed9033d64c2d4e890eb1a25ed6e7a26024f74fd
class FallDetector:
    def __init__(self, tflite_path, yolo_path, frame_count=8):
        # ... (giữ nguyên phần load model) ...
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
        self.email_sent_for_this_event = False # Quan trọng: Tránh gửi mail liên tục khi đang ngã
        self.dismissed = False
        self.email_sender = EmailSender()
        self.email_file = "emails.txt"

    def get_recipients(self):
        """Hàm đọc danh sách email từ file txt"""
        if not os.path.exists(self.email_file):
            return []
        with open(self.email_file, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]

    def process_frame(self, frame, frame_id):
        if frame_id % 2 != 0:
            return frame
<<<<<<< HEAD
            
=======
>>>>>>> aed9033d64c2d4e890eb1a25ed6e7a26024f74fd
        frame_small = cv2.resize(frame, (192, 192))
        results = self.pose_model.predict(frame_small, imgsz=192, conf=0.2, verbose=False)
            
        if len(results[0].boxes) == 0:
            self.last_label = "NORMAL"
            self.last_prob = 0.0
            self.fall_start_time = None # Reset nếu không thấy người
            self.email_sent_for_this_event = False

        else:
            # --- Vẽ Bounding Box (giữ nguyên logic của bạn) ---
            h_orig, w_orig = frame.shape[:2]
<<<<<<< HEAD
            box = results[0].boxes.xyxy[0].cpu().numpy() 
            x1, y1, x2, y2 = box
=======
            # Lấy thông tin box đầu tiên
            box = results[0].boxes.xyxy[0].cpu().numpy() 
            x1, y1, x2, y2 = box
            # Lấy kích thước ảnh 
>>>>>>> aed9033d64c2d4e890eb1a25ed6e7a26024f74fd
            img_h_yolo, img_w_yolo = results[0].orig_shape 
            scale_x, scale_y = w_orig / img_w_yolo, h_orig / img_h_yolo
            cv2.rectangle(frame, (int(x1*scale_x), int(y1*scale_y)), (int(x2*scale_x), int(y2*scale_y)), (0, 0, 255), 2)

            # --- Xử lý Pose & Fall Detection ---
            if len(results[0].keypoints) > 0:
                keypoints = results[0].keypoints.xy[0].cpu().numpy().flatten()
                self.sequence.append(keypoints)
                if len(self.sequence) > self.FRAME_COUNT:
                    self.sequence.pop(0)

                if len(self.sequence) == self.FRAME_COUNT:
                    input_data = np.array(self.sequence, dtype=np.float32).reshape(1, self.FRAME_COUNT, 34)
                    self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
                    self.interpreter.invoke()
                    output = self.interpreter.get_tensor(self.output_details[0]['index'])
                    
                    prob = float(output[0][0])
                    self.last_prob = prob

                    if prob > 0.98:
                        self.last_label = "FALL"
                        if self.fall_start_time is None:
                            self.fall_start_time = time.time()
                            self.captured_frame = None 
                            self.email_sent_for_this_event = False # Reset cho sự kiện mới

                        elapsed = time.time() - self.fall_start_time

<<<<<<< HEAD
                        # Chụp ảnh bằng chứng
                        if 2.0 <= elapsed <= 2.5 and self.captured_frame is None:
                            self.captured_frame = frame.copy()
=======
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
>>>>>>> aed9033d64c2d4e890eb1a25ed6e7a26024f74fd

                        # Gửi mail sau 10 giây nếu chưa dismiss và chưa gửi cho lần ngã này
                        if elapsed >= 10.0 and not self.dismissed and not self.email_sent_for_this_event:
                            recipients = self.get_recipients()
                            if recipients:
                                frame_to_send = self.captured_frame if self.captured_frame is not None else frame
                                ok, buffer = cv2.imencode(".png", frame_to_send)
                                if ok:
                                    img_bytes = buffer.tobytes()
                                    threading.Thread(
                                        target=self.email_sender.send_email_bytes,
                                        args=(recipients, img_bytes),
                                        daemon=True
                                    ).start()
                                
                                self.email_sent_for_this_event = True # Đánh dấu đã gửi
                                print(f"📧 Đã gửi cảnh báo tới {len(recipients)} email.")
                    else:
                        # Reset trạng thái khi đứng dậy (NORMAL)
                        self.last_label = "NORMAL"
                        self.fall_start_time = None
                        self.captured_frame = None 
                        self.email_sent_for_this_event = False
                        if self.dismissed:
                            self.dismissed = False # Sẵn sàng cho lần ngã tiếp theo
                    print(self.dismissed)
        return frame

    def draw_label(self, frame):
        # ... (giữ nguyên) ...
        color = (0, 0, 255) if self.last_label == "FALL" else (0, 255, 0)
        cv2.putText(frame, f"{self.last_label} {self.last_prob:.2f}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return frame