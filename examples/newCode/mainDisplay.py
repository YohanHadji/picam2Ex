import numpy as np

from communication import *
from camera import *
from display import *

camInit()
UDPInit("display")

while True:
    # Get a frame with metadata
    frame, sensorTimeStamp = getFrame()

    parseIncomingData()

    show_all_name_at_position(frame, LightPointArray)
    cv2.showImage('frame', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
