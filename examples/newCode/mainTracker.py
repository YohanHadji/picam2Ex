import numpy as np

from communication import *
from detection import * 
from camera import *

camInit()
UDPInit("tracker")

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

    # Fill light point array
    for i, (name, firstSeen, x, y, _, _, _, _, _) in enumerate(all_light_points):
        LightPointArray[i] = LightPoint(name=name, isVisible=firstSeen, x=x, y=y)

    sendListToRaspi(LightPointArray)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
