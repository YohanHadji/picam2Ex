from flask import Flask, render_template, request
from camera import *
import cv2

camInit(30)

app = Flask(__name__)

# Initialize a dictionary to store input values
input_values = {}

@app.route('/')
def index():
    return render_template('index.html')

def process_frame(frame, processing_type):
    if processing_type == "original":
        return frame
    elif processing_type == "black_and_white":
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, processed_frame = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)
        return processed_frame
    elif processing_type == "contour_with_points":
        # Perform contour detection and draw points
        contours, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cX, cY), 5, (0, 255, 0), -1)
        return frame

def gen_frames(processing_type):
    while True:
        # Capture the frame
        frame = picam2.capture_array()
        processed_frame = process_frame(frame, processing_type)

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
    app.run(debug=True, host='0.0.0.0', port=8000)