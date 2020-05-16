import paho.mqtt.client as mqtt

from .config import settings

def publish_mqtt(payload):
    client = mqtt.Client()
    client.connect(settings["MQTT_SERVER"],
                   settings["MQTT_SERVER_PORT"])
    client.publish(settings["BROKER_TOPIC"], payload)
    client.disconnect()


def check_exclude_callsign_list(callsign):
    return any(callsign.startswith(key) for key in settings["EXCLUDE_CALLSIGNS"])

def locator_to_latlong(locator):
    locator = locator.upper()

    if len(locator) == 5 or len(locator) < 4:
        return ValueError

def defined_frequencies(freq):
    return freq in settings["FREQUENCIES"]