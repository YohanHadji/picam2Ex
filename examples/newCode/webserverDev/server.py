from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO
import numpy as np
from communication import *
from camera import *
import cv2
import time

app = Flask(__name__)
socketio = SocketIO(app)

camInit(30)

input_values = {}

def generate_frames():
    while True:
        frame = picam2.capture_array()
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()
        socketio.emit('video_frame', {'frame': frame_data})
        time.sleep(0.1)  # Adjust the sleep time as needed to control the frame rate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_variable', methods=['POST'])
def update_variable():
    global input_values
    data = request.get_json()
    input_id = data['id']
    input_value = int(data['value'])

    if input_values.get(input_id) != input_value:
        print(f"Value for {input_id} changed to {input_value}")

    input_values[input_id] = input_value

    return "Variable updated successfully!"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(target=generate_frames)

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    finally:
        picam2.stop()