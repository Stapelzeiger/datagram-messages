import msgpack
import threading


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


class ConnectionHandler:

    class CallTimeout(Exception):
        pass

    def __init__(self, insock, outsock=None):
        if outsock is None:
            outsock = insock
        self.insock = insock
        self.outsock = outsock
        self.sendlock = threading.Lock()
        self.handlerlock = threading.Lock()
        self.call_seq_nbr = 0
        self.call_timeout = 0.5
        self.call_nb_retries = 3
        self.active_service_calls = {}
        self.service_handlers = {}
        self.message_handlers = {}
        self.default_message_handler = lambda msg, arg: None

    def set_msg_handler(self, msg, handler):
        '''
        register a message handler callback
        the handler is called with the received message as argument
        '''
        with self.handlerlock:
            self.message_handlers[msg] = handler

    def set_default_msg_handler(self, handler):
        '''
        register a default message handler callback
        this handler is called when no handler has been set for a received message
        it is called with message name and argument
        '''
        with self.handlerlock:
            self.default_message_handler = handler

    def set_service_handler(self, service, handler):
        '''
        register a service handler callback
        the handler is called with the received message as argument and
        and the return value is sent as the response
        '''
        with self.handlerlock:
            self.service_handlers[service] = handler

    def service_call(self, service, arg):
        '''
        perform a remote service call
        '''
        with self.handlerlock:
            seq = self.call_seq_nbr
            self.call_seq_nbr = seq + 1

            res_signal = threading.Event()
            self.active_service_calls[(service, seq)] = {'res': None, 'sig': res_signal}

            nb_retries = self.call_nb_retries
            timeout = self.call_timeout

        for i in range(nb_retries):
            with self.sendlock:
                self.outsock.send(encode('req', [service, seq, arg]))
            if res_signal.wait(timeout):
                with self.handlerlock:
                    return self.active_service_calls.pop((service, seq))['res']

        # remove service call from list
        self.active_service_calls.pop((service, seq))
        raise self.CallTimeout('{} timed out. timeout {}s x {} retries'.format(service, timeout, nb_retries))

    def send(self, name, msg):
        '''
        send a message
        '''
        if name in ('req', 'res'):
            raise ValueError('reserved message name {}'.format(name))
        with self.sendlock:
            self.outsock.send(encode(name, msg))

    def _handle_service_req(self, arg):
        service_name, seq, request_arg = arg
        with self.handlerlock:
            if service_name in self.service_handlers:
                res = self.service_handlers[service_name](request_arg)
                res_datagram = encode('res', [service_name, seq, res])
                with self.sendlock:
                    self.outsock.send(res_datagram)

    def _handle_service_res(self, arg):
        service_name, seq, response_arg = arg
        with self.handlerlock:
            if (service_name, seq) in self.active_service_calls:
                self.active_service_calls[(service_name, seq)]['res'] = response_arg
                self.active_service_calls[(service_name, seq)]['sig'].set()

    def _handle_message(self, name, msg):
        with self.handlerlock:
            if name in self.message_handlers:
                self.message_handlers[name](msg)
            else:
                self.default_message_handler(name, msg)

    def handle_datagram(self, datagram):
        name, arg = decode(datagram)
        if name == 'req':
            self._handle_service_req(arg)
        elif name == 'res':
            self._handle_service_res(arg)
        else:
            self._handle_message(name, arg)

    def spin_forever(self):
        while True:
            self.handle_datagram(self.insock.recv(1024))

    def start_daemon(self):
        t = threading.Thread(target=self.spin_forever)
        t.daemon = True
        t.start()
