import cv2
import os
from flask import Flask, Response, render_template, jsonify, request, redirect

class WebApp:
    def __init__(self, camera, detector):
        self.app = Flask(__name__)
        self.camera = camera
        self.detector = detector
        self.frame_id = 0
        self.email_file = "emails.txt" # File lưu danh sách email

        # Khai báo các route hiện có
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video', 'video', self.video)
        self.app.add_url_rule('/status', 'status', self.status)
        self.app.add_url_rule('/dismiss', 'dismiss', self.dismiss)
        
        # Thêm các route mới để quản lý Email
        self.app.add_url_rule('/settings', 'settings', self.settings)
        self.app.add_url_rule('/add_email', 'add_email', self.add_email, methods=['POST'])
        self.app.add_url_rule('/delete_email/<email>', 'delete_email', self.delete_email)

    # --- Logic quản lý Email ---
    def get_email_list(self):
        if not os.path.exists(self.email_file):
            return []
        with open(self.email_file, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]

    def settings(self):
        emails = self.get_email_list()
        # Bạn cần tạo file settings.html hoặc gộp chung vào index.html
        return render_template("settings.html", emails=emails)

    def add_email(self):
        new_email = request.form.get('email')
        if new_email:
            emails = self.get_email_list()
            if new_email not in emails:
                with open(self.email_file, "a") as f:
                    f.write(new_email + "\n")
        return redirect('/settings')

    def delete_email(self, email):
        emails = self.get_email_list()
        if email in emails:
            emails.remove(email)
            with open(self.email_file, "w") as f:
                for e in emails:
                    f.write(e + "\n")
        return redirect('/settings')

    # --- Các hàm cũ giữ nguyên ---
    def generate_frames(self):
        while True:
            frame = self.camera.get_frame()
            if frame is None: continue
            self.frame_id += 1
            frame = self.detector.process_frame(frame, self.frame_id)
            frame = self.detector.draw_label(frame)
            display_frame = cv2.resize(frame, (480, 360)) 
            ret, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   buffer.tobytes() + b'\r\n')

    def index(self):
        return render_template("index.html")

    def video(self):
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def dismiss(self):
        self.detector.dismissed = True
        return "Alert dismissed successfully"

    def status(self):
        return jsonify({
            "label": self.detector.last_label,
            "prob": self.detector.last_prob
        })

    def run(self):
        self.app.run(host="0.0.0.0", port=5001, threaded=True)