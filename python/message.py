import msgpack


def encode(name, arg, msgpack_opt={'use_single_float': True}):
    """
    Encode a message datagram
    """
    return msgpack.packb([name, arg], **msgpack_opt)


def decode(datagram, msgpack_opt={'encoding': 'ascii'}):
    """
    Decode a message datagram, returns tuple (name, arg)
    """
    msg = msgpack.unpackb(datagram, **msgpack_opt)
    return msg[0], msg[1]
