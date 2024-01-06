from flask import Flask, render_template, Response, request
import numpy as np
import threading
import cv2
import socket
from communication import *
from camera import *

app = Flask(__name__)

# Light point structure
class LightPoint:
    def __init__(self, name, isVisible, x, y):
        self.name = str(name)
        self.isVisible = bool(isVisible)  # Ensure boolean type
        self.x = int(x)  # Ensure integer type
        self.y = int(y)  # Ensure integer type

# Create an array of structures without specifying values
LightPointArray = [LightPoint(name="ABCD", isVisible=False, x=0, y=0) for _ in range(10)]

camInit(30)

# Initialize a dictionary to store input values
input_values = {}

def udp_listener():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 8888

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        # Decode the data with capsule
        for byte in data:
            capsule_instance.decode(byte)

def process_frame(frame, processing_type):
    if processing_type == "original":
        return frame
    elif processing_type == "black_and_white":
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, processed_frame = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)
        return processed_frame
    elif processing_type == "contour_with_points":
        # Perform contour detection and draw points
        contours, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cX, cY), 5, (0, 255, 0), -1)
        return frame

def gen_frames(processing_type):
    global LightPointArray

    while True:
        # Capture the frame
        frame = picam2.capture_array()

        if newPacketReceived():
            packetType = newPacketReceivedType()
            if packetType == "pointList":
                LightPointArray = returnLastPacketData(packetType)

        processed_frame = process_frame(frame, processing_type)

        # Encode the frame
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + processed_frame_bytes + b'\r\n')

@app.route('/video_feed/<processing_type>')
def video_feed(processing_type):
    return Response(gen_frames(processing_type), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flask():
    app.run(host='0.0.0.0', port=8000, threaded=True)

if __name__ == '__main__':
    try:
        udp_thread = threading.Thread(target=udp_listener)
        flask_thread = threading.Thread(target=run_flask)

        udp_thread.start()
        flask_thread.start()

        flask_thread.join()  # Wait for Flask thread to finish (which won't happen as it runs indefinitely)
    finally:
        picam2.stop()