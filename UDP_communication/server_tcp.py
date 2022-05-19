from socket import *


host = "172.17.0.4" # docker server
port = 6007         # forwarding: 14007 -> 6007

# External -> Internal -> Docker (IP)
# 각각엔 모두 다른 IP와 Port number를 가지고 있다.


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((host, port))
serverSocket.listen(1)
print("Wait for receiving data from clinet...")

connectionSocket, addr = serverSocket.accept()
print("Connected to", str(addr))

data = connectionSocket.recv(1024)
msg = data.decode("utf8")
print("Received Data:", msg)

msg = msg.upper()

connectionSocket.send(msg.encode("utf8"))
print("Send to message")

serverSocket.close()
