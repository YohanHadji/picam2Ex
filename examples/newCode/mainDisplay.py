from flask import Flask, render_template, Response
import numpy as np
import threading 

from communication import *
from camera import *
import cv2
import time

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

def udp_listener():
    UDP_IP = "0.0.0.0"  # Escuchar en todas las interfaces
    UDP_PORT = 8888 # Puerto en el que escuchar

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024) # Tamaño del buffer es 1024 bytes
        # Decode the data with capsule
        for byte in data:
            capsule_instance.decode(byte)


def gen_frames():

    global LightPointArray

    while True:
        # Capturar el frame
        frame = picam2.capture_array()

        # parseIncomingDataFromUDP()
        if (newPacketReceived()):
            packetType = newPacketReceivedType()
            if (packetType == "pointList"):
                LightPointArray = returnLastPacketData(packetType)

        # # Print the number of elements in the array
        # print(len(LightPointArray))
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _dummy, b_frame = cv2.threshold(gray_frame,128, 255, cv2.THRESH_BINARY)
                
        for point in LightPointArray:
            #cv2.circle(frame, (point.x, point.y), 10, (0, 0, 255), -1)
            cv2.putText(b_frame, point.name, (point.x, point.y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            #print(point.name, point.x, point.y)
                
        # cv2.circle(frame, (10,10), 10, (0, 0, 255), -1)
        # cv2.circle(frame, (100,100), 10, (0, 0, 255), -1)
        # cv2.circle(frame, (200,200), 10, (0, 0, 255), -1)

        # Codificar el frame para la transmisión
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
    # Ruta principal que renderiza la plantilla HTML
    return render_template('index.html')


if __name__ == '__main__':
    try:
        udp_thread = threading.Thread(target=udp_listener)
        udp_thread.start()
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        picam2.stop()