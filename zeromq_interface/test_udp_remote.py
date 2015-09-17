import socket
import sys
import time
import threading
sys.path.append('../python/')
import datagrammessages


UDP_IP_IN = "127.0.0.1"
UDP_IP_OUT = "127.0.0.1"

UDP_PORT_IN = 5005
UDP_PORT_OUT = 5006
print("UDP out IP:", UDP_IP_OUT)
print("UDP out port:", UDP_PORT_OUT)
print("UDP in IP:", UDP_IP_IN)
print("UDP in port:", UDP_PORT_IN)


sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind((UDP_IP_IN, UDP_PORT_IN))

time.sleep(3)

sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_out.connect((UDP_IP_OUT, UDP_PORT_OUT))


s = datagrammessages.ConnectionHandler(sock_in, sock_out)

if sys.argv[1] == 's':
    s.set_msg_handler('test', lambda x: print(x))
    s.set_service_handler('testservice', lambda x: x**2)
    s.spin_forever()


s.start_daemon()

i = 0
while 1:
    i = i+1
    # print('calling test:', i)
    # print(s.service_call('test', i))
    s.send('udp_message', i)
    time.sleep(1)
