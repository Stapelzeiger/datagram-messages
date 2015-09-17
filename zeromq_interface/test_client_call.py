import time
import zmq
import msgpack

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

i = 0
while True:
    req = ['testservice', i]
    socket.send(msgpack.packb(req))
    res = socket.recv()
    print(msgpack.unpackb(res))
    i = i+1
    time.sleep(1)
