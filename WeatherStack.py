import json
import requests
import MQTT
import time

if __name__ == '__main__':

    print("In the main")
    token = "7ffb83bd785a070c3f85b06655b8dbef"
    url = "https://api.weatherstack.com/current?access_key=7ffb83bd785a070c3f85b06655b8dbef"

    city = "Turin"  # TODO: get the city from location

    querystring = {"query": city}

    response = requests.get(url, params=querystring)

    print(response.json())
    with open('weather.json', 'w') as file:
        json.dump(response.json(), file)