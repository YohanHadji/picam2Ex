import cv2
import numpy as np
from picamera2 import Picamera2
import time
import random
import string

# Inicializar Picamera2
picam2 = Picamera2()

# Configuraciones de la cámara
camera_config = picam2.create_video_configuration(main={"format": "BGR888", "size": (800, 606)}, raw={"format": "SRGGB10", "size": (1332, 990)})
picam2.configure(camera_config)
picam2.set_controls({"FrameRate": 120})
# Iniciar la cámara
picam2.start()

prev_time_sec = 0
startTime = time.time()
fpsCounter = 0
all_light_points = []

class MovingAverageCalculator:
    def __init__(self, window_size):
        self.window_size = window_size
        self.window = []
        self.cumulative_sum = 0

    def calculate_moving_average(self, new_value):
        self.window.append(new_value)
        self.cumulative_sum += new_value

        if len(self.window) == self.window_size:
            average = self.cumulative_sum / self.window_size

            # Subtract the oldest value to prepare for the next iteration
            self.cumulative_sum -= self.window[0]
            self.window.pop(0)

            return average

        return None  # Return None until the window is filled

window_size = 500
fpsCalculator = MovingAverageCalculator(window_size)
fpsDeviationCalculator = MovingAverageCalculator(window_size)
fpsAverage = 0
fpsDeviation = 0
previousMetadata = picam2.capture_metadata()

def obtain_top_contours(b_frame, n=10):
    """
    Obtain the top n x and y coordinates of the brightest contours.
    When none is found, it returns a list of (-1, -1).
    """
    try:
        contours, _h = cv2.findContours(b_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        _, contours, _h = cv2.findContours(b_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return [(-1, -1)] * n

    contour_brightness = []

    for blob in contours:
        M = cv2.moments(blob)
        if M['m00'] != 0:
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            contour_brightness.append(((cx, cy), cv2.contourArea(blob)))

    # Sort contours based on brightness
    sorted_contours = sorted(contour_brightness, key=lambda x: x[1], reverse=True)

    # Return the top n contours
    top_contours = [point for point, _ in sorted_contours[:n]]

    return top_contours


def is_point_close_with_motion_estimation(x1, y1, x2, y2, speed_x1, speed_y1, acceleration_x1, acceleration_y1, timestamp1, timestamp2, threshold):
    """
    Check if two points are close to each other based on the estimated position.
    """
    delta_t_nanosecond = timestamp2 - timestamp1
    delta_t = delta_t_nanosecond / 1e9

    # Estimate the next position based on the last known position, speed, and acceleration for both x and y
    estimated_x = x1 + speed_x1 * delta_t + 0.5 * acceleration_x1 * delta_t/1e9**2
    estimated_y = y1 + speed_y1 * delta_t + 0.5 * acceleration_y1 * delta_t/1e9**2

    # The threshold for each axis should be adjusted depending on the speed and acceleration of the object
    thresholdx = 50
    thresholdy = 50

    # The allowed position range should be an ellipse with angle the speed vector angle and the major axis the norm of the speed vector and the minor axis a constant

    # Check if the new position is close to the estimated position
    position_close = abs(x2 - estimated_x) <= thresholdx and abs(y2 - estimated_y) <= thresholdy

    return position_close

def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def estimate_position(last_position, speed_x, speed_y, acceleration_x, acceleration_y, last_timestamp, current_timestamp):
    """
    Estimate the current position based on the last known position, speed, and acceleration for both x and y.
    """
    delta_t_nanosecond = current_timestamp - last_timestamp
    delta_t = delta_t_nanosecond / 1e9

    estimated_x = last_position[0] + speed_x * delta_t + 0.5 * acceleration_x * delta_t**2
    estimated_y = last_position[1] + speed_y * delta_t + 0.5 * acceleration_y * delta_t**2

    return estimated_x, estimated_y

def calculate_speed_and_acceleration(last_position, current_position, last_timestamp, current_timestamp):
    """
    Calculate speed and acceleration given the last and current positions and timestamps for each coordinate (x and y).
    """
    if last_position is None or last_timestamp is None:
        return 0, 0, 0, 0  # Initial values for speed and acceleration

    delta_t_nanosecond = current_timestamp - last_timestamp
    delta_t = delta_t_nanosecond / 1e9
    if delta_t == 0:
        return 0, 0, 0, 0  # Avoid division by zero

    delta_x = current_position[0] - last_position[0]
    delta_y = current_position[1] - last_position[1]

    # Calculate speed and acceleration for both x and y coordinates
    speed_x = delta_x / delta_t
    speed_y = delta_y / delta_t

    acceleration_x = speed_x / delta_t
    acceleration_y = speed_y / delta_t

    return speed_x, speed_y, acceleration_x, acceleration_y

def process_and_store_light_points(new_points, sensorTimeStamp):
    global all_light_points

    # Get the current timestamp
    current_time = sensorTimeStamp

    # Process new points
    for new_x, new_y in new_points:
        point_found = False

        for i, (existing_name, existing_firstSeen, existing_x, existing_y, existing_timestamp, existing_speed_x, existing_speed_y, existing_acceleration_x, existing_acceleration_Y)in enumerate(all_light_points):
            if is_point_close_with_motion_estimation(existing_x, existing_y, new_x, new_y, existing_speed_x, existing_speed_y, existing_acceleration_x, existing_acceleration_Y, existing_timestamp, current_time, 50):
                # Replace old point values with the most recent and compute new acceleration and speed
                speed_x, speed_y, acceleration_x, acceleration_y = calculate_speed_and_acceleration((existing_x, existing_y), (new_x, new_y), existing_timestamp, current_time)
                #  print("Point %d updated: (%d, %d, %f, %f, %f, %f)" % (i + 1, new_x, new_y, speed_x, speed_y, acceleration_x, acceleration_y))
                all_light_points[i] = (existing_name, existing_firstSeen, new_x, new_y, current_time, speed_x, speed_y, acceleration_x, acceleration_y)
                point_found = True
                break

        if not point_found:
            # Add new point to the list with acceleration and speed = 0 for both x and y
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            # Make sure the name doesn't already exist in the current list:
            while name in [existing_name for existing_name, _, _, _, _, _, _, _, _ in all_light_points]:
                name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))

            all_light_points.append((name, current_time, new_x, new_y, current_time, 0, 0, 0, 0))

    all_light_points = [(name, firstSeen, x, y, timestamp, speed_x, speed_y, acceleration_x, acceleration_y) for name, firstSeen, x, y, timestamp, speed_x, speed_y, acceleration_x, acceleration_y in all_light_points if current_time - timestamp <= 1e9]


while True:
    # Capturar el frame
    request = picam2.capture_request()
    frame = request.make_array("main")
    #frame = picam2.capture_array("main")
    metadata = request.get_metadata()
    request.release()

    sensorTimeStamp = metadata['SensorTimestamp']

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _dummy, b_frame = cv2.threshold(gray_frame,128, 255, cv2.THRESH_BINARY) ### gustavo

    result = obtain_top_contours(b_frame, 10)
    process_and_store_light_points(result, sensorTimeStamp)

    # Print only the first 3 light points with their name, position x and y only.
    for i, (name, firstSeen, x, y, timestamp, speed_x, speed_y, acceleration_x, acceleration_y) in enumerate(all_light_points[:3]):
        print("Point %d: (%s, %d, %d)" % (i + 1, name, x, y, speed_x, speed_y, acceleration_x, acceleration_y))

    # Tiempo actual
    current_time_sec = time.time()

    # Calcular el framerate
    if prev_time_sec != 0:
        fps = 1 / (current_time_sec - prev_time_sec)
        fpsAverage = fpsCalculator.calculate_moving_average(fps)
        if fpsAverage is not None:
            fpsDeviation = fpsDeviationCalculator.calculate_moving_average(abs(fpsAverage-fps))
            if fpsDeviation is not None:
                print(round(fpsAverage), round(fpsDeviation), sensorTimeStamp)

    prev_time_sec = current_time_sec
    previousMetadata = metadata

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cerrar todas las ventanas
cv2.destroyAllWindows()
picam2.stop()
