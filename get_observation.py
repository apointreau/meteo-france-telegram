from environment import *
import requests
from get_forecast import icon_to_emoji


METEOFRANCE_API_URL = "http://webservice.meteofrance.com/observation"


def get_current_observation(place):

    params = {"token": METEOFRANCE_API_TOKEN,
              "lat": place.latitude,
              "lon": place.longitude}

    return requests.get(url=METEOFRANCE_API_URL, params=params).json()


def pretty_print_current_observation(current_weather):

    pretty_printed_results = "En ce moment : " + \
        current_weather['observation']['weather']['desc']

    if icon_to_emoji.get(str(current_weather['observation']['weather']['icon'])) != None:
        pretty_printed_results += " " + \
            icon_to_emoji.get(
                current_weather['observation']['weather']['icon'])
    else:
        pretty_printed_results += " " + \
            current_weather['observation']['weather']['icon']

    pretty_printed_results += ", " + \
        str(current_weather['observation']['T'])+"°C.\n\n"

    return pretty_printed_results
