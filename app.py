import cv2
from flask import Flask, Response, render_template, jsonify


class WebApp:
    def __init__(self, camera, detector):
        self.app = Flask(__name__)
        self.camera = camera
        self.detector = detector
        self.frame_id = 0

        # Khai báo route
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video', 'video', self.video)
        self.app.add_url_rule('/status', 'status', self.status)
        self.app.add_url_rule('/dismiss', 'dismiss', self.dismiss)
    def generate_frames(self):
        while True:
            frame = self.camera.get_frame()
            if frame is None:
                continue

            self.frame_id += 1

            frame = self.detector.process_frame(frame, self.frame_id)
            frame = self.detector.draw_label(frame)
            display_frame = cv2.resize(frame, (480, 360)) 
            ret, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            #ret, buffer = cv2.imencode('.jpg', frame)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   buffer.tobytes() + b'\r\n')

    def index(self):
        return render_template("index.html")

    def video(self):
        return Response(
            self.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    def dismiss(self):
        self.detector.dismissed = True
        print("Alert dismissed")
        return "Alert dismissed successfully"
    def status(self):
        return jsonify({
            "label": self.detector.last_label,
            "prob": self.detector.last_prob
        })

    def run(self):
        self.app.run(host="0.0.0.0", port=5001, threaded=True)