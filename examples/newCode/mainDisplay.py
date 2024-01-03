from flask import Flask, render_template, Response
import numpy as np

from communication import *
from camera import *
from display import *

app = Flask(__name__)

camInit()
UDPInit("display")

def gen_frames():
    prev_time = 0
    while True:
        # Capturar el frame
        frame = picam2.capture_array()

        show_all_name_at_position(frame, LightPointArray)

        parseIncomingData()

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