import logging
import json
import socketserver

from .config import settings
from .util import publish_mqtt, callsign_dx_validated, defined_frequencies
from .WSJTX import WSJTXPacket, WSJTXDecodePacket, WSJTXStatusPacket

logger = logging.getLogger(__name__)


class WSJTXUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        datagram = self.request[0].strip()
        self.parse_datagram(datagram)

    def parse_datagram(self, datagram):
        wsjtxmsg = WSJTXPacket.from_udp_packet(datagram)

        # We need to be aware of the current frequency but this doesn't appear within decode packets
        # In order to get the current frequency, handle a status message first and then allow decode messages
        if type(wsjtxmsg) is WSJTXStatusPacket:
            # check and make sure that the currentFreq is allowed within our settings
            # if it is then set the dial_freq variable within the server
            if defined_frequencies(wsjtxmsg.dial_freq):
                self.server._dial_freq = wsjtxmsg.dial_freq

        elif type(wsjtxmsg) is WSJTXDecodePacket and self.server._dial_freq:
            msg_content = wsjtxmsg.content

            # Look for messages with the following format
            # CQ <CALLSIGN> <LOCATOR>
            if msg_content.startswith('CQ') and msg_content.count(' ') == 2:
                _, callsign, locator = msg_content.split(" ")

                # only publish to mqtt if it meets the following conditions
                # Meets MIN_DX setting
                # Not in the exclude callsign list
                # The setting to only display new callsigns has been enabled
                if callsign_dx_validated(self.server._dial_freq, callsign, locator, wsjtxmsg.newcall):
                    payload = json.dumps(
                        {"callsign":callsign,
                         "locator":locator,
                         "snr": wsjtxmsg.snr,
                         "freq": self.server._dial_freq
                         }
                    )
                    publish_mqtt(payload)


class WSJTXDecodeServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        self._dial_freq = None
        socketserver.UDPServer.__init__(self, server_address, RequestHandlerClass)


def start_udp_server():
    logger.debug("Starting UDP server")
    server = WSJTXDecodeServer((settings["SERVER_IP"],
                                settings["SERVER_PORT"]), WSJTXUDPHandler)
    server.serve_forever()


if __name__ == "__main__":
    start_udp_server()
