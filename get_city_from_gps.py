from environment import *
import requests


def get_current_city_from_gps(latitude, longitude):

    params = {"latitude": latitude,
              "longitude": longitude,
              "localityLanguage": "fr"}

    return requests.get(url=GPS_API_URL, params=params).json().get('locality')
