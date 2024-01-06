from flask import Flask, render_template, Response, request, stream_with_context
import numpy as np
from communication import *
from camera import *
import cv2
import time

app = Flask(__name__)

camInit(30)

input_values = {}  # Assuming you have a global dictionary to store input values

def generate_frames():
    while True:
        frame = picam2.capture_array()
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        #time.sleep(0.1)  # Adjust the sleep time as needed to control the frame rate

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/update_variable', methods=['POST'])
# def update_variable():
#     global input_values
#     data = request.get_json()
#     input_id = data['id']
#     input_value = int(data['value'])

#     if input_values.get(input_id) != input_value:
#         print(f"Value for {input_id} changed to {input_value}")

#     input_values[input_id] = input_value

#     return "Variable updated successfully!"

@app.route('/update_variable', methods=['POST'])
def update_variable():
    global slider_value
    data = request.get_json()
    slider_value = int(data['value'])
    return "Variable updated successfully!"

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        picam2.stop()