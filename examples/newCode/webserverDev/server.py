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

def gen_frames():
    global LightPointArray

    while True:
        # Capture the frame
        frame = picam2.capture_array()

        if newPacketReceived():
            packetType = newPacketReceivedType()
            if packetType == "pointList":
                LightPointArray = returnLastPacketData(packetType)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, b_frame = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)

        for point in LightPointArray:
            cv2.putText(b_frame, point.name, (point.x, point.y), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)

        # Encode the frame
        _, buffer = cv2.imencode('.jpg', b_frame)
        b_frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + b_frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/update_variable', methods=['POST'])
def update_variable():
    global input_values
    data = request.get_json()
    input_id = data['id']
    input_value = int(data['value'])

    # Check if the value has changed
    if input_values.get(input_id) != input_value:
        print(f"Value for {input_id} changed to {input_value}")

    # Update the input_values dictionary
    input_values[input_id] = input_value

    return "Variable updated successfully!"

if __name__ == '__main__':
    try:
        udp_thread = threading.Thread(target=udp_listener)
        udp_thread.start()
        app.run(host='0.0.0.0', port=8000, threaded=True)
    finally:
        picam2.stop()