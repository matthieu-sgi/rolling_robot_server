import socket

#Listens for incoming connections on port 3000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 3000))
server.listen(5)
print('Listening on localhost:3000')
print('Waiting for connection')
client, addr = server.accept()
print(f'Connected to {addr}')
