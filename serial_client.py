import serial
import queue
import os
import threading

class SerialClient:
    def __init__(self):
        self.run = False
        self.sending_queue = queue.Queue()
        self.receiving_queue = queue.Queue()
        self.serial_comm = self.open_port()

        self.start()

    
    def start(self) -> None:
        self.run = True
        
        
        self.receiving_thread = threading.Thread(target=self._receiving_thread)
        self.sending_thread = threading.Thread(target=self._sending_thread)
        
        self.receiving_thread.start()
        self.sending_thread.start()
    
    def open_port(self) -> serial.Serial:
        files = os.listdir('/dev')
        port = ""
        for devices in files:
            if devices.startswith('ttyACM'):
                port = f'/dev/{devices}'
        print(port)
        return serial.Serial(
            port=port,
            baudrate=230400,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1
        )
    
    def send_message(self, data) -> None:
        self.sending_queue.put(data)
    
    def get_message(self) -> str:
        try:
            msg = self.receiving_queue.get(block=True)
        except queue.Empty:
            msg = None
        return msg
    
    def _receiving_thread(self) -> None :
        while self.run:
            data = self.serial_comm.read_until(b"\n")
            self.receiving_queue.put(data)
    
    def _sending_thread(self) -> None:
        while self.run:
            data : str = self.sending_queue.get(block=True)
            self.serial_comm.write(data.encode(encoding='ascii'))
    
    def stop(self) -> None:
        self.run = False
        
        self.receiving_thread.join(timeout=0.1)
        self.sending_thread.join(timeout=0.1)