'''module that define the server side of the tcp connection'''

import socket

class TcpServer:
    '''class that define the server side of the tcp connection'''
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f'Listening on {self.host}:{self.port}')
        print('Waiting for connection')
        # self.client = None
        # while self.client is None:
        self.client, self.addr = self.server.accept()
        # self.client, self.addr = self.server.accept()
        print(f'Connected to {self.addr}')

    def send(self, data : str):
        '''send data to the client'''
        self.client.send(data.encode(encoding='ascii'))

    def receive(self) -> str:
        '''receive data from the client'''
        return self.client.recv(1024).decode(encoding='ascii')
    