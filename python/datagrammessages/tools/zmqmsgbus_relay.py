import logging
import time
import zmqmsgbus
import datagrammessages
from datagrammessages import SerialConnection
import argparse
import uuid
import serial.tools.list_ports
import sys
import glob
import serial


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def find_serial_connection_for_device_name(devname):
    ports = serial_ports()
    for port in ports:
        print('checking port ' + port)
        conn = SerialConnection(port)
        conn.start_daemon()
        name = serial_conntction_get_device_name(conn)
        if name == devname:
            print(devname + ' found on port ' + port)
            return conn
    raise Exception('could not find device with name ' + devname)


def serial_conntction_get_device_name(conn):
    try:
        return conn.service_call('name', None)
    except datagrammessages.ConnectionHandler.CallTimeout:
        return 'unknown-' + str(uuid.uuid1())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='relay datagram-message connection to a zmqmsgbus')
    parser.add_argument('--from', dest='from_addr', nargs='*',
                        default=['ipc://ipc/source'])
    parser.add_argument('--to', dest='to_addr', nargs='*',
                        default=['ipc://ipc/sink'])
    parser.add_argument('--rename', default=None)
    parser.add_argument('--services', nargs='*', help='services to advertise',
                        default=[])
    parser.add_argument('--sub', '--subscribe', nargs=2,
                        metavar=('TOPIC', 'MESSAGE_NAME'),
                        help='subscribe to topic', action='append',
                        default=[])
    parser.add_argument('dev', help='serial device path or device name')

    args = parser.parse_args()

    time.sleep(1)
    logging.basicConfig(level=logging.DEBUG)

    if args.dev.startswith('/dev/tty'):
        conn = SerialConnection(args.dev)
        conn.start_daemon()
        name = serial_conntction_get_device_name(conn)
    else:
        name = args.dev
        conn = find_serial_connection_for_device_name(name)

    if args.rename is None:
        zmq_name = '/' + name + '/'
    else:
        zmq_name = '/' + args.rename + '/'

    services = args.services
    forward_topics = dict(args.sub)

    bus = zmqmsgbus.Bus(sub_addr='ipc://ipc/source',
                        pub_addr='ipc://ipc/sink')
    node = zmqmsgbus.Node(bus)

    # publish datagram-messages to zmqmsgbus
    msg_pub = lambda msg, content: node.publish(zmq_name + msg, content)
    conn.set_default_msg_handler(msg_pub)

    # forward zmqmsgbus service calls over datagram-messages
    def service_call(service, req):
        try:
            logging.debug('calling service ' + service)
            ret =  conn.service_call(service, req)
            logging.debug('done ' + service)
            return ret
        except datagrammessages.ConnectionHandler.CallTimeout as e:
            logging.debug('call failed ' + str(e))
            raise zmqmsgbus.ServiceFailed(str(e))

    handlers = []
    for service in services:
        handler = lambda req, service=service: service_call(service, req)
        handlers.append(handler)
        node.register_service(zmq_name + service, handler)

    # forward zmqmsgbus topics to datagram-messages
    def fwd_topic(topic, msg):
        conn.send(forward_topics[topic], msg)

    for topic in forward_topics:
        node.register_message_handler(topic, fwd_topic)

    while True:
        time.sleep(1)
