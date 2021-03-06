import unittest
import datagrammessages.connection_handler as conn
import msgpack
import threading
from unittest.mock import MagicMock, Mock, patch


class MessageEncodeTestCase(unittest.TestCase):

    def test_encode(self):
        self.assertEqual(conn.encode('test', 42),
                         msgpack.packb(['test', 42]))


class MessageDecodeTestCase(unittest.TestCase):

    def test_decode(self):
        self.assertEqual(conn.decode(msgpack.packb(['test', 42])),
                         ('test', 42))


class ConnectionHandlerTestCase(unittest.TestCase):

    @patch('datagrammessages.threading.Thread')
    def setUp(self, thread_mock):
        self.s = conn.ConnectionHandler()

    def test_send(self):
        self.s.sock_send = Mock()
        self.s.send('test', 'foo')
        self.s.sock_send.assert_called_with(msgpack.packb(['test', 'foo']))

    @patch('datagrammessages.threading.Thread')
    def test_send_reserved_name(self, thread_mock):
        with self.assertRaisesRegex(ValueError, 'reserved message name req'):
            conn.ConnectionHandler().send('req', None)
        with self.assertRaisesRegex(ValueError, 'reserved message name res'):
            conn.ConnectionHandler().send('res', None)

    def test_handle_datagram(self):
        self.s._handle_service_req = MagicMock()
        self.s._handle_service_res = MagicMock()
        self.s._handle_message = MagicMock()
        self.s.handle_datagram(conn.encode('req', ['test', 1234, 'args']))
        self.s._handle_service_req.assert_called_once_with(['test', 1234, 'args'])
        self.s.handle_datagram(conn.encode('res', ['test', 1234, 'args']))
        self.s._handle_service_res.assert_called_once_with(['test', 1234, 'args'])
        self.s.handle_datagram(conn.encode('test', 'foo'))
        self.s._handle_message.assert_called_once_with('test', 'foo')

    def test_handle_message(self):
        handler = MagicMock()
        self.s.set_msg_handler('test', handler)
        self.s.handle_datagram(conn.encode('test', 'foo'))
        handler.assert_called_once_with('foo')

    def test_default_nonexisting_message(self):
        self.s.handle_datagram(conn.encode('test', 'foo'))

    def test_default_message_handler(self):
        handler = MagicMock()
        self.s.set_default_msg_handler(handler)
        self.s.handle_datagram(conn.encode('foo', 123))
        handler.assert_called_once_with('foo', 123)

    def test_handle_service(self):
        self.s.sock_send = Mock()
        handler = MagicMock(return_value=42)
        self.s.set_service_handler('test', handler)
        self.s.handle_datagram(conn.encode('req', ['test', 1234, '6*9']))
        handler.assert_called_once_with('6*9')
        expected_result = conn.encode('res', ['test', 1234, 42])
        self.s.sock_send.assert_called_once_with(expected_result)

    @patch.object(threading.Event, 'wait', autospec=True)
    def test_service_call(self, event_wait_mock):
        self.s.sock_send = Mock()

        expected_req = conn.encode('req', ['test', 0, 'arg'])
        resp = conn.encode('res', ['test', 0, 'result'])

        def side_effect(self_, timeout):
            self.s.handle_datagram(resp)
            return True

        event_wait_mock.side_effect = side_effect

        self.assertEqual(self.s.service_call('test', 'arg'), 'result')
        self.s.sock_send.assert_called_once_with(expected_req)
        # event_wait_mock.assert_called_once_with(0.5)

    @patch('datagrammessages.threading.Thread')
    @patch.object(threading.Event, 'wait', autospec=True)
    def test_service_call_timeout(self, event_wait_mock, thread_mock):
        self.s.sock_send = Mock()

        event_wait_mock.return_value = False
        with self.assertRaisesRegex(conn.ConnectionHandler.CallTimeout,
                                    'servicename timed out. timeout 0.5s x 3 retries'):
            self.s.service_call('servicename', 'arg')
