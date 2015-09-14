import zmq
import time
import sys
import msgpack

context = zmq.Context()


sender = context.socket(zmq.PUB)
sender.connect("tcp://localhost:5558")

i = 0
while True:
    msg = msgpack.packb(sys.argv[1]) + msgpack.packb(i)
    sender.send(msg)
    time.sleep(1)
    i += 1
