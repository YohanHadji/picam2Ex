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

    arrayToSend = bytearray(10*17)
    packet_id = 0x02

    # Fill light point array
    for i, (name, firstSeen, x, y, _, _, _, _, _) in enumerate(all_light_points[:10]):
        byteToSend = struct.pack('4sbii', name.encode('utf-8'), firstSeen, x, y)
        # Concatenate the byte array 
        arrayToSend[i*len(byteToSend):(i+1)*len(byteToSend)] = byteToSend
    
    payload_data = arrayToSend
    packet_length = len(payload_data)
    encoded_packet = capsule_instance.encode(packet_id, payload_data, packet_length)
    # Convert encoded_packet to a bytearray
    encoded_packet = bytearray(encoded_packet)
    # Send the encoded packet
    sock.sendto(encoded_packet, (OTHER_RASPI_IP, OTHER_RASPI_PORT))

    #sendListToRaspi(LightPointArray)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
