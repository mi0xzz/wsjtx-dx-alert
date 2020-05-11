import socket
import struct
import json
import paho.mqtt.client as mqtt
from config import settings

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

        return struct.unpack('>Q', b)

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
        self._buffer.read(1)                # new decode
        self._buffer.read(4)                # time
        self._snr = self._buffer.read_int() # snr
        self._buffer.read(8)                # delta time
        self._buffer.read(4)                # delta freq
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

        dialfreq = self._buffer.read_longlong()
        mode = self._buffer.read_string()


class WSJTXHearbeatPacket:
    def __init__(self, data):
        WSJTXPacket.__init__(self, data)

        self._buffer.read(4)
        self._version = self._buffer.read_string()
        self._revision = self._buffer.read_string()


def publish_mqtt(payload):
    client = mqtt.Client()
    client.connect(settings["MQTT_SERVER"],
                   settings["MQTT_SERVER_PORT"])
    client.publish(settings["BROKER_TOPIC"], payload)
    client.disconnect()


def verify_dx(callsign):
    dx = True
    for e in settings["EXCLUDE_CALLSIGNS"]:
        if callsign.startswith(e):
            dx = False
            break
    return dx


def start_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((settings["SERVER_IP"],
               settings["SERVER_PORT"]))

    while True:
        data, addr = sock.recvfrom(1024)
        wsjtxmsg = WSJTXPacket.from_udp_packet(data)

        if type(wsjtxmsg) is WSJTXDecodePacket:
            msgcontent = wsjtxmsg.content

            # Look for messages with the following format
            # CQ <CALLSIGN> <LOCATOR>
            if msgcontent.startswith('CQ') and msgcontent.count(' ') == 2:
                _, callsign, locator = msgcontent.split(" ")

                # only publish to mqtt if it's really DX
                # so check the exclude callsign list first
                if verify_dx(callsign):
                    payload = json.dumps(
                        {"callsign":callsign,
                         "locator":locator,
                         "snr": wsjtxmsg.snr
                         }
                    )
                    publish_mqtt(payload)


def main():
    start_udp_server()


if __name__ == "__main__":
    main()