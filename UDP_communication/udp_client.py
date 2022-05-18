'''    
'''

CLIENT_PORT_NUMBER = 14007


# import socket library
import socket
import sys
from timeit import default_timer as timer

# Create UDP socket to send to server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
read = sys.stdin.readline



while True:
    
    # input from keyboard
    # (ex) -1 0 1
    # 각각의 데이터는 문자
    data = [i for i in input("Input >> ").split()]
    msg = "".join(data)

    if msg == "quit":
        sock.close()
        break

    # send message encoded to server(IP and port)  
    print("send to message...")
    sock.sendto(msg.encode(), ("192.168.50.90", CLIENT_PORT_NUMBER))
    
    # get message and address
    print("receive message from server...")
    recvMsg, addr = sock.recvfrom(2048)
    
    # print message decoded
    print("Completed!")
    print(recvMsg.decode())
    
    received_data = recvMsg.decode()

    print("Received data type: {}".format(type(received_data)))

    # close socket
    if(recvMsg.decode() == "0"):
        sock.close()
        break

print("Client is terminated.")
# from socket import *


# serverName = 'hostname'
# serverPort = 12000
# clientSocket = socket(AF_INET, SOCK_DGRAM)
# message = raw_input('Input lowercase sentence:')
# clientSocket.sendto(message.encode(), serverName, serverPort)
# modifiedMessage, severAddress = clientSocket.recvfrom(2048)
# print(modifiedMessage.decode())
# clientSocket.close()
