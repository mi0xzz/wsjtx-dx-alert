import paho.mqtt.client as mqtt

from .config import settings

def publish_mqtt(payload):
    client = mqtt.Client()
    client.connect(settings["MQTT_SERVER"],
                   settings["MQTT_SERVER_PORT"])
    client.publish(settings["BROKER_TOPIC"], payload)
    client.disconnect()