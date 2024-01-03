from flask import Flask, render_template, Response
import cv2
import numpy as np
from picamera2 import Picamera2
import time

app = Flask(__name__)

# Inicializar Picamera2
picam2 = Picamera2()
#config = picam2.create_video_configuration(raw={'format': 'SRGGB10', 'size': (1332, 990)})
camera_config = picam2.create_video_configuration(main={"format": "BGR888", "size": (800, 606)}, raw={"format": "SRGGB10", "size": (1332, 990)})
picam2.configure(camera_config)
picam2.start()

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
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        picam2.stop()