import numpy as np
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

UDP_IP_TRACKER = "192.168.1.11"
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

newControllerPacketReceived = False
newPointListPacketReceived = False

# Light point structure
LightPoint = namedtuple('LightPoint', ['name','isVisible', 'x', 'y'])
# Create an array of structures without specifying values
LightPointArray = [LightPoint(name="ABCD", isVisible=False, x=0, y=0) for _ in range(10)]

# Example of using the Capsule class
class Foo:
    pass

def newPacketReceived():
    global newControllerPacketReceived, newPointListPacketReceived
    return newControllerPacketReceived or newPointListPacketReceived

def newPacketReceivedType():
    global newControllerPacketReceived, newPointListPacketReceived
    if (newControllerPacketReceived):
        return "controller"
    if (newPointListPacketReceived):
        return "pointList"

def returnLastPacketData(packetType):
    global joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight, LightPointArray, newControllerPacketReceived, newPointListPacketReceived
    if (packetType == "controller"):
        newControllerPacketReceived = False
        return joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight
    elif (packetType == "pointList"):
        newPointListPacketReceived = False
        return LightPointArray

def handle_packet(packetId, dataIn, lenIn):
    global joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight, LightPointArray, newControllerPacketReceived, newPointListPacketReceived
    #print(f"Received packet {packetId}: {dataIn[:lenIn]}")
    print(len(bytearray(dataIn)))
    # Joystick packet received
    if (packetId == 0x01):
        newControllerPacketReceived = True
         # Assuming the first 4 bytes are preamble data, and the rest is 2 floats and 5 bools
        joystickX, joystickY, joystickBtn, swUp, swDown, swLeft, swRight = struct.unpack('ffbbbbb', dataIn) 
    # List of tracked points packet
    elif (packetId == 0x02):
        newPointListPacketReceived = True
        print("Received list of tracked points")
        LightPointArray = struct.unpack('4sbii'*10, bytearray(dataIn))

capsule_instance = Capsule(lambda packetId, dataIn, len: handle_packet(packetId, dataIn[:len], len))

def UDPInit(name):
    global sock
    if (name == "tracker"):
        sock.bind((UDP_IP_TRACKER, UDP_PORT))
    elif (name == "display"):
        sock.bind((UDP_IP_DISPLAY, UDP_PORT))
    sock.setblocking(0)

def sendTargetToTeensy(pointToSend):
    global sock
    # Send the target point to the teensy, the structure should be copied in a byte array then encoded then sent
    packet_id = 0x01
    # Pack the struct in a byte array
    pointToSendName = str(pointToSend.name)
    payload_data = struct.pack('4sbii', pointToSendName.encode('utf-8'), np.uint8(pointToSend.isVisible), np.int32(pointToSend.x), np.int32(pointToSend.y))
    packet_length = len(payload_data)
    encoded_packet = capsule_instance.encode(packet_id, payload_data, packet_length)
    # Print the encoded packet
    print(f"Encoded Packet: {encoded_packet}")
    # Convert encoded_packet to a bytearray
    encoded_packet = bytearray(encoded_packet)
    # Send the encoded packet
    sock.sendto(encoded_packet, (TEENSY_IP, TEENSY_PORT))

def sendLightPointListToRaspi(all_light_points, n):
    global sock

    # Light point structure
    LightPoint = namedtuple('LightPoint', ['name','isVisible', 'x', 'y'])
    # Create an array of structures without specifying values
    LightPointArray = [LightPoint(name="ABCD", isVisible=False, x=0, y=0) for _ in range(n)]

    # Print only the first 3 light points with their name, position x and y only.
    for i, (name, _, x, y, _, speed_x, speed_y, acceleration_x, acceleration_y) in enumerate(all_light_points[:n]):
        print("Point %d: (%s, %d, %d, %d, %d, %d, %d)" % (i + 1, name, x, y, speed_x, speed_y, acceleration_x, acceleration_y))
        LightPointArray[i] = LightPoint(name, 1, x, y)

    arrayToSend = bytearray()
    byteToSend = bytearray()
    packet_id = 0x02
    
    # Fill light point array
    for i, point in enumerate(LightPointArray):
        pointToSend = LightPoint(point.name, point.isVisible, point.x, point.y)
        pointToSendName = str(point.name)
        byteToSend = struct.pack('4sbii', pointToSendName.encode('utf-8'), np.uint8(pointToSend.isVisible), np.int32(pointToSend.x), np.int32(pointToSend.y))
        # Concatenate the byte to the array
        arrayToSend[i*16:(i+1)+16] = byteToSend

    payload_data = arrayToSend
    packet_length = len(arrayToSend)
    encoded_packet = capsule_instance.encode(0x02, payload_data, packet_length)
    # Convert encoded_packet to a bytearray
    encoded_packet = bytearray(encoded_packet)
    sock.sendto(encoded_packet, (OTHER_RASPI_IP, OTHER_RASPI_PORT))

def parseIncomingDataFromUDP():
    global sock
    try:
        data, addr = sock.recvfrom(1024)  # Adjust the buffer size as needed
        print(f"Received {len(data)} bytes from {addr}")

        # Decode the data with capsule
        for byte in data:
            capsule_instance.decode(byte)

    except socket.error as e:
        pass
