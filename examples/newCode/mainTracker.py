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

    arrayToSend = bytearray(10*13)
    packet_id = 0x02

    # Fill light point array
    for i, (name, _, x, y, _, _, _, _, _) in enumerate(all_light_points[:10]):
        byteToSend = struct.pack('4sbii'*10, LightPointArray)
        payload_data = byteToSend
        packet_length = len(payload_data)
        encoded_packet = capsule_instance.encode(0x02, payload_data, packet_length)
        # Convert encoded_packet to a bytearray
        encoded_packet = bytearray(encoded_packet)
        sock.sendto(encoded_packet, (OTHER_RASPI_IP, OTHER_RASPI_PORT))
        #sock.sendto(encoded_packet, (GUSTAVO_IP, 8888))

    #sendListToRaspi(LightPointArray)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
