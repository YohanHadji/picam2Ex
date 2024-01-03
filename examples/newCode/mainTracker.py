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
    byteToSend = bytearray(13)
    packet_id = 0x02

    # Fill light point array
    for i, (name, _, x, y, _, _, _, _, _) in enumerate(all_light_points[:10]):
        pointToSend = LightPointArray[i]
        byteToSend = struct.pack('4sbii', pointToSend.name.encode('utf-8'), pointToSend.isVisible, pointToSend.x, pointToSend.y)
        # Concatenate the byte to the array
        arrayToSend[i*13:(i+1)+13] = byteToSend
        #sock.sendto(encoded_packet, (GUSTAVO_IP, 8888))

    payload_data = arrayToSend
    packet_length = len(arrayToSend)
    print(f"Payload data len: {packet_length}")
    encoded_packet = capsule_instance.encode(0x02, payload_data, packet_length)
    # Convert encoded_packet to a bytearray
    encoded_packet = bytearray(encoded_packet)
    sock.sendto(encoded_packet, (OTHER_RASPI_IP, OTHER_RASPI_PORT))

    #sendListToRaspi(LightPointArray)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
