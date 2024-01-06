from flask import Flask, render_template, request
from picamera2 import Picamera2
import cv2

app = Flask(__name__)

# Initialize a dictionary to store input values
input_values = {}

picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"format": "BGR888", "size": (800, 606)}, raw={"format": "SRGGB10", "size": (1332, 990)})
picam2.configure(camera_config)
picam2.set_controls({"FrameRate": 30})
picam2.start()

@app.route('/')
def index():
    return render_template('index.html')

def process_frame(frame, processing_type):
    if processing_type == "original":
        return frame

def gen_frames(processing_type):
    while True:
        # Capture the frame
        frame = picam2.capture_array()
        processed_frame = process_frame(frame, "original")

        # Encode the frame
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + processed_frame_bytes + b'\r\n')

@app.route('/video_feed/<processing_type>')
def video_feed(processing_type):
    return Response(gen_frames(processing_type), mimetype='multipart/x-mixed-replace; boundary=frame')

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
        app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
    finally:
        picam2.stop()
    