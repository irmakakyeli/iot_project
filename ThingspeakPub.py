import requests
import json
import time
from MQTT import MQTT as client

class ThingspeakPub:
    def __init__(self, client_id, broker, port, api_key):
        self.api_key = api_key
        self.client = client(client_id, broker, port, self)
        self.client.start()

    def sub(self, topic):
        self.topics.append(topic)
        self.client.mySubscribe(topic)

    def notify(self, topic, payload):
        data = json.loads(payload)
        uv = data.get("uv", None)
        if uv is None:
            return

        try:
            user = topic.split("/")[1]
        except IndexError:
            return

        # Send to Thingspeak
        url = "https://api.thingspeak.com/update"
        params = {
            "api_key": self.api_key,
            "field1": uv
        }

        response = requests.post(url, params=params)
        if response.status_code == 200:
            print(f"[{user}] 📡 UV {uv} sent to Thingspeak.")
        else:
            print(f"[{user}] ❌ Failed to send to Thingspeak: {response.status_code}")

if __name__ == "__main__":
    api_key = "13CIECX36KEC3GXI"
    client_id = "thingspeakPub"
    broker = "mqtt.eclipseprojects.io"
    port = 1883

    publisher = ThingspeakPub(client_id, broker, port, api_key)
    publisher.sub("UVAlert/+/uv")  # Subscribe to all user UV updates

    while True:
        time.sleep(1)