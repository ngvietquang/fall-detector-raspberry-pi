
import cv2
import threading


class CameraStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src,cv2.CAP_V4L2)
        self.frame = None
        self.running = True

        # Tạo thread đọc frame liên tục
        threading.Thread(target=self._update, daemon=True).start()

    def _update(self):
        #Luồng chạy nền đọc frame (không backlog)
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def get_frame(self):
        return self.frame