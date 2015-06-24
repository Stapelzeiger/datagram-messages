import unittest
import message
import msgpack

class MessageEncodeTestCase(unittest.TestCase):

    def test_encode(self):
        self.assertEqual(message.encode('test', 42),
                         msgpack.packb(['test', 42]))

class MessageDecodeTestCase(unittest.TestCase):

    def test_decode(self):
        self.assertEqual(message.decode(msgpack.packb(['test', 42])),
                         ('test', 42))
