from collections import namedtuple
from capsule import *
import socket

teensyIP = "192.168.1.100"
teensyPort = 8888

# Example of using the Capsule class
class Foo:
    pass

def handle_packet(packetId, dataIn, len):
    print(f"Received packet {packetId}: {dataIn[:len]}")

capsule_instance = Capsule(lambda packetId, dataIn, len: handle_packet(packetId, dataIn, len))

# Light point structure
LightPoint = namedtuple('LightPoint', ['name','isVisible' 'x', 'y'])

# Create an array of structures without specifying values
LightPointArray = [LightPoint(None, None, None) for _ in range(10)]