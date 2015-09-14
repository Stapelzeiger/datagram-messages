import zmq
import msgpack
import sys
sys.path.append('../python/')
import datagrammessages



context = zmq.Context()

msg_receiver = context.socket(zmq.SUB)
msg_receiver.bind("tcp://*:5558")
msg_receiver.setsockopt(zmq.SUBSCRIBE, b'')

msg_publisher_sock = context.socket(zmq.PUB)
msg_publisher_sock.bind("tcp://*:5556")


def publish_on_sock(sock, msg_name, content):
    sock.send(msgpack.packb(msg_name) + msgpack.packb(content))

msg_pub = lambda msg, content: publish_on_sock(msg_publisher_sock, msg, content)


import socket
UDP_IP_IN = "127.0.0.1"
UDP_IP_OUT = "127.0.0.1"
UDP_PORT_IN = 5006
UDP_PORT_OUT = 5005
sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_out.connect((UDP_IP_OUT, UDP_PORT_OUT))
sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind((UDP_IP_IN, UDP_PORT_IN))

conn = datagrammessages.ConnectionHandler(sock_in, sock_out)
conn.set_default_msg_handler(msg_pub)
conn.start_daemon()

while True:
    buf = msg_receiver.recv()
    unpacker = msgpack.Unpacker()
    unpacker.feed(buf)
    msg, content = tuple(unpacker)
    print('sending msg {}: {}'.format(msg, content))
    conn.send(msg, content)

    # hack: publish what we receive
    conn.handle_datagram(datagrammessages.encode(msg, content))
