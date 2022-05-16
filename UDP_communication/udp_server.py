'''
    client와 server 모두 socket를 열어주고, client에서 server host와의 port로 
    Datagram을 생성한다.
    
    server에서는 datagram을 read하여 socket을 이용하여 server host와 port로 반환한다.

    다시 client에서 socket으로부터 받은 datagram을 read하여 값을 얻는다.

    
    이하 코드는 모든 문자열을 대문자로 바꾸어준다.    
    
'''
SERVER_PORT_NUMBER = 20000

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
    if(data.encode() == "0"):
        sock.close()
        break

print("Server is terminated.")