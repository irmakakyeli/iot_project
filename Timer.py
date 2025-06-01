import json
import time
import threading
from MQTT import MQTT as client

class Timer():
    def __init__(self, client_id, broker, port):
        self.client = client(client_id, broker, port, self)
        self.client.start()
        time.sleep(1)
        self.topics = []
        self.status = False
        self.timers = {}  # To manage timers per user/topic

    def sub(self, topic):
        self.topics.append(topic)
        self.client.mySubscribe(topic)

    def notify(self, topic, payload):
        data = json.loads(payload)
        uv = data.get("uv", 0)

        # Extract user from topic
        try:
            user = topic.split("/")[1]
        except IndexError:
            return

        if uv >= 4:
            print(f"[{user}] High UV index detected: {uv}")
            self.start_timer(user)
        else:
            print(f"[{user}] UV index normal: {uv}")
            self.cancel_timer(user)

    def start_timer(self, user):
        if user in self.timers:
            self.timers[user].cancel()

        def send_reminder():
            print(f"[{user}] ⏰ Time to reapply sunscreen!")
            self.client.myPublish(f"UVAlert/{user}/reminder", {"reminder": "Time to reapply sunscreen!"})
            del self.timers[user]

        # Set a timer for 3 hours (3 * 60 * 60)
        timer = threading.Timer(3 * 60 * 60, send_reminder)
        timer.start()
        self.timers[user] = timer
        print(f"[{user}] Timer started for 3 hours.")

    def cancel_timer(self, user):
        if user in self.timers:
            self.timers[user].cancel()
            del self.timers[user]
            print(f"[{user}] Timer canceled due to low UV.")


if __name__ == '__main__':
    print("In the main")

    client_id = 'timer'
    broker = "mqtt.eclipseprojects.io"
    port = 1883
    timer = Timer(client_id, broker, port)
    timer.sub('UVAlert/+/uv')
    while True:
        time.sleep(1)