from capsule import *

# Example of using the Capsule class
class Foo:
    pass

capsule_instance = Capsule(lambda packetId, dataIn, len: print(f"Received packet {packetId}: {dataIn[:len]}"))
capsule_instance.decode(0xFF)
capsule_instance.decode(0xFA)
capsule_instance.decode(0x01)
capsule_instance.decode(0x03)
capsule_instance.decode(0x04)
capsule_instance.decode(0x05)