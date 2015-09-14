# Datagram Messages

This is a very simple protocol to send messages or make service calls using [MessagePack](http://msgpack.org) encoded datagrams.

- Messages are named objects that are sent without any guarantee on delivery.
- Service calls are request/response exchanges between a server and a client.
    Service calls allow to perform reliable communication between the client and the server even in case of packet loss.

Implementations are in C and Python. (The C implementation currently doesn't implement service call client)

The underlying datagram layer can be UDP (only implemented in python) or [serial-datagram](https://github.com/Stapelzeiger/serial-datagram).

## Dependencies

C implementation:

- [cmp_mem_access](https://github.com/Stapelzeiger/cmp_mem_access)
- [cmp](https://github.com/camgunz/cmp.git)
