from flask import Flask, render_template, Response
import numpy as np
import threading 

from communication import *
from camera import *
import cv2
import time

app = Flask(__name__)

camInit(30)

def gen_frames():

    while True:
        # Capture the frame
        frame = picam2.capture_array()
      
        # Encode the frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
        app.run(host='0.0.0.0', port=5000)
    finally:
        picam2.stop()