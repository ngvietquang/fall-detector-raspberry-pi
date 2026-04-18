import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import datetime

class EmailSender:
    def __init__(self):
        self.sender_email = "ngvietquang377@gmail.com"
        self.password = os.getenv("GMAIL_APP_PASSWORD", "uoik ulrr jklx qaba")

        try:
            with open("templates/form_gmail.html", "r", encoding="utf-8") as f:
                self.html_template = f.read()
        except FileNotFoundError:
            self.html_template = "<h2>Canh bao te nga</h2><p>Thoi gian: {time}</p><img src='cid:fall_image'>"

    def send_email_bytes(self, receiver_email, image_bytes):
        msg = MIMEMultipart("related")
        msg["Subject"] = "⚠️ CẢNH BÁO: PHÁT HIỆN TÉ NGÃ"
        msg["From"] = self.sender_email

        if isinstance(receiver_email, list):
            msg["To"] = ", ".join(receiver_email)
            destinations = receiver_email
        else:
            msg["To"] = receiver_email
            destinations = [receiver_email]

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = self.html_template.replace("{time}", now)
        msg.attach(MIMEText(html, "html"))

        img = MIMEImage(image_bytes)
        img.add_header("Content-ID", "<fall_image>")
        img.add_header("Content-Disposition", "inline", filename="fall_event.png")
        msg.attach(img)

        server = None
        try:
            socket.setdefaulttimeout(10)
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, destinations, msg.as_string())
            print(f"✅ Đã gửi cảnh báo thành công tới: {destinations}")
        except Exception as e:
            print(f"❌ Lỗi khi gửi email: {e}")
        finally:
            if server is not None:
                try:
                    server.quit()
                except:
                    pass