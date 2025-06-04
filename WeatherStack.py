import json
import requests
from MQTT import MQTT as client
import time


class WeatherStack():
    def __init__(self, client_id, broker, port):
        self.client = client(client_id, broker, port, self)
        self.client.start()
        time.sleep(1)
        self.topics = []
        self.status = False

    def sub(self, topic):
        self.topics.append(topic)
        self.client.mySubscribe(topic)
    
    

    def notify(self, topic, payload):
        token = "d8744bba0fa5ac2f5e8fd6d16a8045ee" #token change
        url = "https://api.weatherstack.com/current?access_key=d8744bba0fa5ac2f5e8fd6d16a8045ee"
        payload = json.loads(payload)

        try:
            user_id = topic.split("/")[1]
        except IndexError:
            return

        city = payload.get("city", "Turin")
        querystring = {"query": city}

        response = requests.get(url, params=querystring)
        data = response.json()

        print(response.json())
        with open('weather.json', 'w') as file:
            json.dump(data, file)

        # Fake UV index for testing
        uv_index = data.get("current", {}).get("uv_index", 5)

        # Publish to MQTT topic for other components
        self.client.myPublish(f"UVAlert/{user_id}/uv", {"uv": uv_index})

if __name__ == '__main__':
    print("In the main")

    client_id = 'weatherStack'
    broker = "mqtt.eclipseprojects.io"
    port = 1883
    weather = WeatherStack(client_id, broker, port)
    weather.sub('UVAlert/+/location')
    while True:
        time.sleep(1)