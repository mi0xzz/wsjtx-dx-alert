import struct

class ValueBuffer:
    def __init__(self, b):
        self._buffer = b
        self._idx = 0

    def read(self, size):
        b = self._buffer[self._idx:self._idx+size]
        self._idx += size
        return b

    def read_uint(self):
        size = 4
        b = self._buffer[self._idx:self._idx+size]
        self._idx += size

        return struct.unpack('>I', b)[0]

    def read_int(self):
        size = 4
        b = self._buffer[self._idx:self._idx+size]
        self._idx += size

        return struct.unpack('>i', b)[0]

    def read_longlong(self, packed=True):
        size = 8
        b = self._buffer[self._idx:self._idx+size]
        self._idx += size

        return struct.unpack('>Q', b)[0]

    def read_string(self):
        strlen = self.read_uint()
        s = self._buffer[self._idx:self._idx+strlen]
        self._idx += strlen

        return struct.unpack('>{strlen}s'.format(strlen=strlen), s)[0].decode('utf-8')


# http://found.ward.bay.wiki.org/view/udp-reporting-and-requests
class WSJTXPacket:
    def __init__(self, data):
        self._data = data
        self._buffer = ValueBuffer(data)
        self._magicbytes = self._buffer.read_uint()
        self._version = self._buffer.read_uint()
        self._type = self._buffer.read_uint()
        self._id = self._buffer.read_string()

    @classmethod
    def from_udp_packet(cls, data):
        message = cls(data)
        if message._type == 0:
            return WSJTXHearbeatPacket(data)
        elif message._type == 1:
            return WSJTXStatusPacket(data)
        elif message._type == 2:
            return WSJTXDecodePacket(data)

    @property
    def type(self):
        return self._type

    def __repr__(self):
        return self._data.hex()


class WSJTXDecodePacket:
    def __init__(self, data):
        WSJTXPacket.__init__(self, data)

        # skip through most of the packet as don't care about this stuff yet
        self._buffer.read(1)    # new decode
        self._buffer.read(4)                        # time
        self._snr = self._buffer.read_int()         # snr
        self._buffer.read(8)                        # delta time
        self._buffer.read(4)                        # delta freq
        # skip the mode string. need to go back and look at this TODO
        self._buffer.read_string()
        self._message = self._buffer.read_string()

    @property
    def content(self):
        return self._message

    @property
    def snr(self):
        return self._snr


class WSJTXStatusPacket:
    def __init__(self, data):
        WSJTXPacket.__init__(self, data)

        self._dial_freq = self._buffer.read_longlong()
        self._mode = self._buffer.read_string()

    @property
    def dial_freq(self):
        return self._dial_freq


class WSJTXHearbeatPacket:
    def __init__(self, data):
        WSJTXPacket.__init__(self, data)

        self._buffer.read(4)
        self._version = self._buffer.read_string()
        self._revision = self._buffer.read_string()
