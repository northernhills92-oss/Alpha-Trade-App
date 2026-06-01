import requests


def get_fear_greed():

    url = "https://api.alternative.me/fng/"

    data = requests.get(url).json()

    value = int(data['data'][0]['value'])

    if value < 30:
        return "FEAR"

    if value > 70:
        return "GREED"

    return "NEUTRAL"
