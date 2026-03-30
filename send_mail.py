import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import datetime

class EmailSender:
    def __init__(self):

        self.sender_email = ""
        self.receiver_email = ""
        self.password = ""

        self.msg = MIMEMultipart("related")
        self.msg["Subject"] = "Fall Detection Alert"
        self.msg["From"] = self.sender_email
        self.msg["To"] = self.receiver_email

    def send_email(self, image_path):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = open("templates/form_gmail.html").read().replace("{time}", now)

        self.msg.attach(MIMEText(html, "html"))

        with open(image_path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", "<fall_image>")
        self.msg.attach(img)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.sender_email, self.password)

        server.sendmail(self.sender_email, self.receiver_email, self.msg.as_string())
        server.quit()