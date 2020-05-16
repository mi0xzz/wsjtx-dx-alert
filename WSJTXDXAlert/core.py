import logging
import json
import socketserver

from .config import settings
from .util import publish_mqtt, check_exclude_callsign_list, defined_frequencies
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
        if type(wsjtxmsg) is WSJTXStatusPacket and not self.server._currentFreq:
            # check and make sure that the currentFreq is allowed within our settings
            # if it is then set the current_freq variable within the server
            if defined_frequencies(wsjtxmsg.current_freq):
                self.server._currentFreq = wsjtxmsg.current_freq

        elif type(wsjtxmsg) is WSJTXDecodePacket and self.server._currentFreq:
            msg_content = wsjtxmsg.content

            # Look for messages with the following format
            # CQ <CALLSIGN> <LOCATOR>
            if msg_content.startswith('CQ') and msg_content.count(' ') == 2:
                _, callsign, locator = msg_content.split(" ")

                # only publish to mqtt if it's really DX
                # so check the exclude callsign list first
                if not check_exclude_callsign_list(callsign):
                    payload = json.dumps(
                        {"callsign":callsign,
                         "locator":locator,
                         "snr": wsjtxmsg.snr
                         }
                    )
                    publish_mqtt(payload)


class WSJTXDecodeServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        self._currentFreq = None
        socketserver.UDPServer.__init__(self, server_address, RequestHandlerClass)


def start_udp_server():
    logger.debug("Starting UDP server")
    server = WSJTXDecodeServer((settings["SERVER_IP"],
                                settings["SERVER_PORT"]), WSJTXUDPHandler)
    server.serve_forever()
