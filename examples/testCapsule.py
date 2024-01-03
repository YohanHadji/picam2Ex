from capsule import *

# Example of using the Capsule class
class Foo:
    pass

capsule_instance = Capsule(lambda packetId, dataIn, len: print(f"Received packet {packetId}: {dataIn[:len]}"))

# Create a packet with payload 0xAB
packet_id = 0x01
payload_data = bytearray([0xAB])
packet_length = len(payload_data)
encoded_packet = capsule_instance.encode(packet_id, payload_data, packet_length)

# Display the encoded packet
print(f"Encoded Packet: {encoded_packet}")

# For all bytes in the encoded packet, decode them one by one
for byte in encoded_packet:
    capsule_instance.decode(byte) 
