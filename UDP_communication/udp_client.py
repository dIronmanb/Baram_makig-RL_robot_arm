'''
    client와 server 모두 socket를 열어주고, client에서 server host와의 port로 
    Datagram을 생성한다.
    
    server에서는 datagram을 read하여 socket을 이용하여 server host와 port로 반환한다.

    다시 client에서 socket으로부터 받은 datagram을 read하여 값을 얻는다.

    
    이하 코드는 모든 문자열을 대문자로 바꾸어준다.    
    
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
