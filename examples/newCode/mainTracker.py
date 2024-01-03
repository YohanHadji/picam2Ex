import numpy as np

from communication import *
from detection import * 
from camera import *

camInit()
UDPInit()

while True:
    # Get a frame with metadata
    frame, sensorTimeStamp = getFrame()

    # Detect light points
    detect(frame, sensorTimeStamp)

    printLightPoints(3)
    printFps()

    parseIncomingData()
    pointToSend = getLockedPoint(joystickBtn, swUp, swDown, swLeft, swRight)
    sendTargetToTeensy()

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
