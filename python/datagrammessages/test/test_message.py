import unittest
import datagrammessages.message as message
import msgpack
import threading
from unittest.mock import MagicMock, Mock, patch


class MessageEncodeTestCase(unittest.TestCase):

    def test_encode(self):
        self.assertEqual(message.encode('test', 42),
                         msgpack.packb(['test', 42]))


class MessageDecodeTestCase(unittest.TestCase):

    def test_decode(self):
        self.assertEqual(message.decode(msgpack.packb(['test', 42])),
                         ('test', 42))


class ConnectionHandlerTestCase(unittest.TestCase):

    def test_send(self):
        sock = Mock(spec=['send'])
        s = message.ConnectionHandler(sock)
        s.send('test', 'foo')
        sock.send.assert_called_with(msgpack.packb(['test', 'foo']))

    def test_send_reserved_name(self):
        with self.assertRaisesRegex(ValueError, 'reserved message name req'):
            message.ConnectionHandler(None).send('req', None)
        with self.assertRaisesRegex(ValueError, 'reserved message name res'):
            message.ConnectionHandler(None).send('res', None)

    def test_handle_datagram(self):
        s = message.ConnectionHandler(None)
        s._handle_service_req = MagicMock()
        s._handle_service_res = MagicMock()
        s._handle_message = MagicMock()
        s.handle_datagram(message.encode('req', ['test', 1234, 'args']))
        s._handle_service_req.assert_called_once_with(['test', 1234, 'args'])
        s.handle_datagram(message.encode('res', ['test', 1234, 'args']))
        s._handle_service_res.assert_called_once_with(['test', 1234, 'args'])
        s.handle_datagram(message.encode('test', 'foo'))
        s._handle_message.assert_called_once_with('test', 'foo')

    def test_handle_message(self):
        s = message.ConnectionHandler(None)
        handler = MagicMock()
        s.set_msg_handler('test', handler)
        s.handle_datagram(message.encode('test', 'foo'))
        handler.assert_called_once_with('foo')

    def test_default_nonexisting_message(self):
        s = message.ConnectionHandler(None)
        s.handle_datagram(message.encode('test', 'foo'))

    def test_default_message_handler(self):
        s = message.ConnectionHandler(None)
        handler = MagicMock()
        s.set_default_msg_handler(handler)
        s.handle_datagram(message.encode('foo', 123))
        handler.assert_called_once_with('foo', 123)

    def test_handle_service(self):
        sock = Mock(spec=['send'])
        s = message.ConnectionHandler(sock)
        handler = MagicMock(return_value=42)
        s.set_service_handler('test', handler)
        s.handle_datagram(message.encode('req', ['test', 1234, '6*9']))
        handler.assert_called_once_with('6*9')
        expected_result = message.encode('res', ['test', 1234, 42])
        sock.send.assert_called_once_with(expected_result)

    @patch.object(threading.Event, 'wait', autospec=True)
    def test_service_call(self, event_wait_mock):
        sock = Mock(spec=['send'])
        s = message.ConnectionHandler(sock)

        expected_req = message.encode('req', ['test', 0, 'arg'])
        resp = message.encode('res', ['test', 0, 'result'])

        def side_effect(self, timeout):
            s.handle_datagram(resp)
            return True

        event_wait_mock.side_effect = side_effect

        self.assertEqual(s.service_call('test', 'arg'), 'result')
        sock.send.assert_called_once_with(expected_req)
        # event_wait_mock.assert_called_once_with(0.5)

    @patch.object(threading.Event, 'wait', autospec=True)
    def test_service_call_timeout(self, event_wait_mock):
        sock = Mock(spec=['send'])
        s = message.ConnectionHandler(sock)

        event_wait_mock.return_value = False
        with self.assertRaisesRegex(message.ConnectionHandler.CallTimeout,
                                    'servicename timed out. timeout 0.5s x 3 retries'):
            s.service_call('servicename', 'arg')
