from math import radians, sin, cos, atan2, sqrt

import paho.mqtt.client as mqtt

from .config import settings

def publish_mqtt(payload):
    client = mqtt.Client()
    client.connect(settings["MQTT_SERVER"],
                   settings["MQTT_SERVER_PORT"])
    client.publish(settings["BROKER_TOPIC"], payload)
    client.disconnect()


def defined_frequencies(freq):
    if freq in settings["BANDS"]:
        return True
    else:
        return False


def exclude_callsign(current_freq, callsign):
    band_settings = get_band_settings(current_freq)
    if "EXCLUDE_CALLSIGNS" in band_settings:
        return any(callsign.startswith(key) for key in band_settings["EXCLUDE_CALLSIGNS"])

    return False

def min_distance(current_freq, dxlocator):
    band_settings = get_band_settings(current_freq)
    if "MIN_DX" in band_settings:
        min_dx = band_settings["MIN_DX"]
        myloc = settings["MY_LOCATOR"]
        dx = calculate_grid_distance(myloc, dxlocator)

        if dx > min_dx:
            return True
        else:
            return False

    # if MIN_DX is not specified then return True
    return True

def get_band_settings(current_freq):
    if current_freq in settings["BANDS"]:
        return settings["BANDS"][current_freq]
    else:
        return None


def callsign_dx_validated(current_freq, callsign, locator):
    if not exclude_callsign(current_freq, callsign) and min_distance(current_freq, locator):
        return True
    else:
        return False


def maidenhead_locator_to_latlong(locator):
    locator = locator.upper()

    if len(locator) == 5 or len(locator) < 4:
        raise ValueError

    if ord(locator[0]) > ord('R') or ord(locator[0]) < ord('A'):
        raise ValueError

    if ord(locator[1]) > ord('R') or ord(locator[1]) < ord('A'):
        raise ValueError

    if ord(locator[2]) > ord('9')  or ord(locator[2]) < ord('0'):
        raise ValueError

    if ord(locator[3]) > ord('9') or ord(locator[3]) < ord('0'):
        raise ValueError

    longitude = (ord(locator[0]) - ord('A')) * 20 - 180
    latitude = (ord(locator[1]) - ord('A')) * 10 - 90
    longitude += (ord(locator[2]) - ord('0')) * 2
    latitude += (ord(locator[3]) - ord('0'))

    longitude += 1
    latitude += 0.5

    return latitude, longitude


def calculate_grid_distance(locA, locB):

    R = 6371 # radius of the earth
    lat1, lon1 = maidenhead_locator_to_latlong(locA)
    lat2, lon2 = maidenhead_locator_to_latlong(locB)

    dlat = radians(lat2) - radians(lat1)
    dlong = radians(lon2) - radians(lon1)

    rlat1 = radians(lat1)
    rlat2 = radians(lat2)

    # Haversine formula
    a = sin(dlat/2) * sin(dlat/2) + cos(rlat1) * cos(rlat2) * sin(dlong/2) * sin(dlong/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c

    # return miles instead of km so divide by 1.609344
    return d/1.609344

