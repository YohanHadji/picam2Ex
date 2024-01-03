from flask import Flask, render_template, Response
import numpy as np
import threading 

from communication import *
from camera import *

app = Flask(__name__)

camInit()
# UDPInit("display")

# while True:
#     # Capturar el frame
#     frame = picam2.capture_array()

#     show_all_name_at_position(frame, LightPointArray)

#     parseIncomingData()

#     _, buffer = cv2.imencode('.jpg', frame)
#     frame = buffer.tobytes()

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cv2.destroyAllWindows()
# picam2.stop()

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
            # print("Mensaje recibido:")


def gen_frames():
    prev_time = 0
    while True:
        # Capturar el frame
        frame = picam2.capture_array()

        # Procesamiento del frame (tu código de procesamiento aquí)
        # ...
        show_all_name_at_position(frame, LightPointArray)


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