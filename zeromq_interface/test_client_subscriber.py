import sys
import zmq
import msgpack

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:5556")
socket.setsockopt(zmq.SUBSCRIBE, msgpack.packb(sys.argv[1]))

while True:
    buf = socket.recv()
    unpacker = msgpack.Unpacker()
    unpacker.feed(buf)
    print(tuple(unpacker)[1])
