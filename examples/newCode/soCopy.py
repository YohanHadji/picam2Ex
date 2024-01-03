from flask import Flask, render_template, Response
import cv2
import numpy as np
from picamera2 import Picamera2
import time
import socket
import threading
app = Flask(__name__)

# Inicializar Picamera2
picam2 = Picamera2()
#config = picam2.create_video_configuration(raw={'format': 'SRGGB10', 'size': (1332, 990)})
camera_config = picam2.create_video_configuration(main={"format": "XRGB8888", "size": (1280, 720)})
picam2.configure(camera_config)
picam2.start()

def udp_listener():
    UDP_IP = "0.0.0.0"  # Escuchar en todas las interfaces
    UDP_PORT = 8888 # Puerto en el que escuchar

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024) # Tamaño del buffer es 1024 bytes
        print("Mensaje recibido")


def gen_frames():
    prev_time = 0
    while True:
        # Capturar el frame
        frame = picam2.capture_array()

        # Procesamiento del frame (tu código de procesamiento aquí)
        # ...

        # Codificar el frame para la transmisión
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
    # Ruta principal que renderiza la plantilla HTML
    return render_template('index.html')


if __name__ == '__main__':
    try:
        udp_thread = threading.Thread(target=udp_listener)
        udp_thread.start()
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        picam2.stop()
