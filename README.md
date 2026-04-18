# 🏃‍♂️ Real-time Fall Detection System using YOLOv8-pose

A high-performance, real-time fall detection system optimized for edge computing devices (Raspberry Pi). This project leverages **YOLOv8-pose** and **TensorFlow Lite** to ensure low latency and high accuracy.

## 🌟 Key Features
* **Pose Estimation:** Utilizes YOLOv8-pose to track 17 keypoints of the human skeleton.
* **Fall Detection Algorithm:** Logic based on rapid changes in the center of gravity, bounding box aspect ratio, and body angle.
* **Edge AI Optimization:** Models are converted to `.tflite` format for smooth execution on Raspberry Pi 4/5.
* **Web Dashboard:** Integrated monitoring interface built with **Flask** for remote video streaming.

## 🛠 Tech Stack
* **Language:** Python 3.9+
* **AI Frameworks:** Ultralytics (YOLOv8), TensorFlow Lite Runtime.
* **Libraries:** OpenCV, NumPy, Flask.
* **Hardware:** Raspberry Pi 4/5, Camera Module / USB Webcam.

## 📥 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ngvietquang/fall-detector-raspberry-pi.git](https://github.com/ngvietquang/fall-detector-raspberry-pi.git)
    cd fall-detector-raspberry-pi
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install opencv-python ultralytics tflite-runtime flask
    ```

## 🚀 How to Run
To start the detection system and the web server:
```bash
python src/main.py
