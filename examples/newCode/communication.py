from collections import namedtuple
from capsule import *
import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

TEENSY_IP = "192.168.1.100"
TEENSY_PORT = 8888

OTHER_RASPI_IP = "192.168.1.178"
OTHER_RASPI_PORT = 8888

UDP_IP = "192.168.1.114"
UDP_PORT = 8888

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
LightPointArray = [LightPoint(None, None, None, None) for _ in range(10)]

def handle_packet(packetId, dataIn, len):
    global joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight, LightPointArray
    print(f"Received packet {packetId}: {dataIn[:len]}")
    # Joystick packet received
    if (packetId == 0x01):
         # Assuming the first 4 bytes are preamble data, and the rest is 2 floats and 5 bools
        joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight = struct.unpack('ffbbbbb', dataIn) 
    # List of tracked points packet
    elif (packetId == 0x02):
        # Assuming 10 light points
        LightPointArray = struct.unpack('cbii'*10, dataIn)

capsule_instance = Capsule(lambda packetId, dataIn, len: handle_packet(packetId, dataIn, len))

def UDPInit():
    global sock
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(0)

def sendTargetToTeensy(pointToSend):
    global sock
    # Send the target point to the teensy, the structure should be copied in a byte array then encoded then sent
    packet_id = 0x01
    # Pack the struct in a byte array
    payload_data = struct.pack('4sbii', pointToSend.name.encode('utf-8'), pointToSend.isVisible, pointToSend.x, pointToSend.y)
    packet_length = len(payload_data)
    encoded_packet = capsule_instance.encode(packet_id, payload_data, packet_length)
    # Send the encoded packet
    sock.sendto(encoded_packet, (TEENSY_IP, TEENSY_PORT))

def sendListToRaspi(listToSend):
    # Send the list of tracked points to the ther raspberry pi. Each point contains a name, a x and y position, and a boolean indicating if the point is visible or not
    packet_id = 0x02
    # Pack the struct in a byte array
    payload_data = struct.pack('4sbii'*len(listToSend), *listToSend)
    packet_length = len(payload_data)
    encoded_packet = capsule_instance.encode(packet_id, payload_data, packet_length)
    # Send the encoded packet
    sock.sendto(encoded_packet, (OTHER_RASPI_IP, OTHER_RASPI_PORT))

def parseIncomingData():
    global sock
    try:
        data, addr = sock.recvfrom(1024)  # Adjust the buffer size as needed

        # Decode the data with capsule
        for byte in data:
            capsule_instance.decode(byte)

    except socket.error as e:
        pass