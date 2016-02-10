import serial
import serial_datagram
import time
import datagrammessages


class SerialConnection(datagrammessages.ConnectionHandler):

    def __init__(self, serial_device, baudrate=115200):
        if isinstance(serial_device, str):
            self.dev_path = serial_device
            self.baud = baudrate
            self.open()
        else:
            self.dev_path = None
            self.dev = serial_device
        super(SerialConnection, self).__init__()

    def open(self):
        self.dev = serial.Serial(self.dev_path, baudrate=self.baud)

    def reopen(self):
        if self.dev_path is None:
            raise Exception('cannot reopen device, path not specified')
        while True:
            try:
                print("trying to reopen")
                self.dev = serial.Serial(self.dev_path, baudrate=self.baud)
                return
            except serial.SerialException:
                time.sleep(0.5)

    def sock_send(self, pkg):
        try:
            self.dev.write(serial_datagram.encode(pkg))
        except serial.SerialException:
            self.reopen()

    def sock_recv(self):
        while True:
            try:
                return serial_datagram.read(self.dev)
            except (serial_datagram.CRCMismatchError, serial_datagram.FrameError):
                print("CRC error")
            except serial.serialutil.SerialException as e:
                print(e)
                self.reopen()
            except TypeError as e: # serial doesn't correctly handle the OSError exception on OS X
                if str(e) == "'OSError' object is not subscriptable":
                    print('serial device error')
                    self.reopen()
                else:
                    raise e
