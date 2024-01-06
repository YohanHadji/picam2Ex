from flask import Flask, render_template, Response
import numpy as np
import threading 

from communication import *
from camera import *
import cv2
import time

app = Flask(__name__)

camInit(30)

# def udp_listener():
#     UDP_IP = "0.0.0.0" 
#     UDP_PORT = 8888

#     sock = socket.socket(socket.AF_INET, # Internet
#                          socket.SOCK_DGRAM) # UDP
#     sock.bind((UDP_IP, UDP_PORT))

#     while True:
#         data, addr = sock.recvfrom(1024) 
#         # Decode the data with capsule
#         for byte in data:
#             capsule_instance.decode(byte)


def gen_frames():

    while True:
        # Capture the frame
        frame = picam2.capture_array()

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _dummy, b_frame = cv2.threshold(gray_frame,200, 255, cv2.THRESH_BINARY)
      
        # Encode the frame
        _, buffer = cv2.imencode('.jpg', b_frame)
        b_frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + b_frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # HTML
    return render_template('index.html')


if __name__ == '__main__':
    try:
        # udp_thread = threading.Thread(target=udp_listener)
        # udp_thread.start()
        app.run(host='0.0.0.0', port=5000)
    finally:
        picam2.stop()