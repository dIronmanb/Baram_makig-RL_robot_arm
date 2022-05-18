# -*- coding: utf-8 -*-

SERVER_PORT_NUMBER = 30000

# import socket library
import socket
from timeit import default_timer as timer

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind port of localhost
# port: type-int, not used port
sock.bind(("127.0.0.1", SERVER_PORT_NUMBER))

while True:
    # Read message and get address of client
    print("Wait for receiving data from client")
    start = timer()
    data, addr = sock.recvfrom(2048)
    

    # Decode message, and convert to capital
    print("Data decoding...")
    data = data.decode().upper()

    # Send to client
    print("Send to data to client...")
    sock.sendto(data.encode(), addr)
    
    # Close socket
    print("Complete")
    if(data == "0"):
        sock.close()
        break

print("Server is terminated.")
