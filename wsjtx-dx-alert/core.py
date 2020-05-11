import logging
import json
import socketserver

from .config import settings
from .util import publish_mqtt
from .WSJTX import WSJTXPacket, WSJTXDecodePacket

logger = logging.getLogger(__name__)

class WSJTXUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        datagram = self.request[0].strip()
        wsjtxmsg = WSJTXPacket.from_udp_packet(datagram)

        if type(wsjtxmsg) is WSJTXDecodePacket:
            msgcontent = wsjtxmsg.content

            # Look for messages with the following format
            # CQ <CALLSIGN> <LOCATOR>
            if msgcontent.startswith('CQ') and msgcontent.count(' ') == 2:
                _, callsign, locator = msgcontent.split(" ")

                # only publish to mqtt if it's really DX
                # so check the exclude callsign list first
                if not exclude_callsign(callsign):
                    payload = json.dumps(
                        {"callsign":callsign,
                         "locator":locator,
                         "snr": wsjtxmsg.snr
                         }
                    )
                    publish_mqtt(payload)


def exclude_callsign(callsign):
    return any(callsign.startswith(key) for key in settings["EXCLUDE_CALLSIGNS"])


def start_udp_server():
    logger.debug("Starting UDP server")
    serverAddress = (settings["SERVER_IP"],
                     settings["SERVER_PORT"])
    serverUDP = socketserver.UDPServer(serverAddress, WSJTXUDPHandler)
    serverUDP.serve_forever()
