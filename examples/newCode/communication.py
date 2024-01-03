
from collections import namedtuple
from capsule import *
from display import *
import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

TEENSY_IP = "192.168.1.100"
TEENSY_PORT = 8888

OTHER_RASPI_IP = "192.168.1.178"
OTHER_RASPI_PORT = 8888

UDP_IP_TRACKER = "192.168.1.114"
UDP_IP_DISPLAY = "192.168.1.178"
UDP_PORT = 8888

GUSTAVO_IP = "192.168.1.181"
GUSTAVO_PORT = 8888

joystickX = 0
joystickY = 0
joystickBtn = 0
swUp = False
swDown = False 
swLeft = False 
swRight = False

# Example of using the Capsule class
class Foo:
    pass

# Light point structure
LightPoint = namedtuple('LightPoint', ['name','isVisible', 'x', 'y'])
# Create an array of structures without specifying values
LightPointArray = [LightPoint(name="ABCD", isVisible=False, x=0, y=0) for _ in range(10)]
pointToSend = LightPoint(name="ABCD", isVisible=False, x=0, y=0)

def show_number_at_position(image, name, cx, cy):
    """
    Show a number at a given position on the image.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    font_color = (0, 0, 255)  # White color for the text

    cv2.putText(image, name, (cx, cy), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

    return image


def show_all_name_at_position(frame):
        global LightPointArray
        print("Puting points on the picture")
        for i, (name, _, x, y) in enumerate(LightPointArray):
            frame = show_number_at_position(frame, name, 10, 10)
            print(f"Point {i+1}: {name} at ({x}, {y})")
        return frame

def handle_packet(packetId, dataIn, lenIn):
    global joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight, LightPointArray
    #print(f"Received packet {packetId}: {dataIn[:lenIn]}")
    print(len(bytearray(dataIn)))
    # Joystick packet received
    if (packetId == 0x01):
         # Assuming the first 4 bytes are preamble data, and the rest is 2 floats and 5 bools
        joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight = struct.unpack('ffbbbbb', dataIn) 
    # List of tracked points packet
    elif (packetId == 0x02):
        print("Received list of tracked points")
        LightPointArray = struct.unpack('4sbii'*10, bytearray(dataIn))
        print(LightPointArray)


capsule_instance = Capsule(lambda packetId, dataIn, len: handle_packet(packetId, dataIn[:len], len))

def UDPInit(name):
    global sock
    if (name == "tracker"):
        sock.bind((UDP_IP_TRACKER, UDP_PORT))
    elif (name == "display"):
        sock.bind((UDP_IP_DISPLAY, UDP_PORT))
    sock.setblocking(0)

def sendTargetToTeensy():
    global sock
    # Send the target point to the teensy, the structure should be copied in a byte array then encoded then sent
    packet_id = 0x01
    # Pack the struct in a byte array
    payload_data = struct.pack('4sbii', pointToSend.name.encode('utf-8'), pointToSend.isVisible, pointToSend.x, pointToSend.y)
    packet_length = len(payload_data)
    encoded_packet = capsule_instance.encode(packet_id, payload_data, packet_length)
    # Print the encoded packet
    print(f"Encoded Packet: {encoded_packet}")
    # Convert encoded_packet to a bytearray
    encoded_packet = bytearray(encoded_packet)
    # Send the encoded packet
    sock.sendto(encoded_packet, (TEENSY_IP, TEENSY_PORT))

def sendListToRaspi(listToSend):
    # Send the list of tracked points to the ther raspberry pi. Each point contains a name, a x and y position, and a boolean indicating if the point is visible or not
    packet_id = 0x02

    # List to send is an array of LightPoint structures
    # For each LightPoint, create one byte array with the structure packed in it
    # Then concatenate all the byte arrays

    # Create a byte array with the size of the list to send
    arrayToSend = bytearray(len(listToSend))

    for i, point in enumerate(listToSend):
        arrayToSend[i] = struct.pack('4sbii', point.name.encode('utf-8'), point.isVisible, point.x, point.y)

    payload_data = arrayToSend
    packet_length = len(payload_data)
    encoded_packet = capsule_instance.encode(packet_id, payload_data, packet_length)
    # Convert encoded_packet to a bytearray
    encoded_packet = bytearray(encoded_packet)
    # Send the encoded packet
    sock.sendto(encoded_packet, (OTHER_RASPI_IP, OTHER_RASPI_PORT))

def parseIncomingData():
    global sock
    try:
        data, addr = sock.recvfrom(1024)  # Adjust the buffer size as needed
        print(f"Received {len(data)} bytes from {addr}")

        # Decode the data with capsule
        for byte in data:
            capsule_instance.decode(byte)

    except socket.error as e:
        pass
