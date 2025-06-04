import requests
import json
import time
from MQTT import MQTT as client

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class ThingspeakPub:
    def __init__(self, client_id, broker, port):
        self.client = client(client_id, broker, port, self)
        self.client.start()
        self.topics = []

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
            users = load_users()
            user_info = users.get(user)
            if not user_info:
                print(f"[{user}] ❌ Not found in users.json.")
                return

            api_key = user_info.get("thingspeak_key")
            if not api_key:
                print(f"[{user}] ❌ Missing Thingspeak key.")
                return

        except Exception as e:
            print(f"[ERROR] while processing user {user}: {e}")
            return

        url = "https://api.thingspeak.com/update"
        params = {
            "api_key": api_key,
            "field1": uv
        }

        response = requests.post(url, params=params)
        if response.status_code == 200:
            print(f"[{user}] 📡 UV {uv} sent to Thingspeak.")
        else:
            print(f"[{user}] ❌ Failed to send to Thingspeak: {response.status_code}")

if __name__ == "__main__":
    client_id = "thingspeakPub"
    broker = "mqtt.eclipseprojects.io"
    port = 1883

    publisher = ThingspeakPub(client_id, broker, port)
    publisher.sub("UVAlert/+/uv")  # Subscribe to all user UV updates

    while True:
        time.sleep(1)