import socket

#Listens for incoming connections on port 3000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 3000))
server.listen(5)
# print('Listening on localhost:3000')
print('Waiting for connection')
while True:
    client, addr = server.accept()
    print(f'Connected to {addr}')
