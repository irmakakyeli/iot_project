import time
from MQTT import MQTT
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import json
import requests

class Mybot():
    def __init__(self, token, client_id, broker, port):
        self.token = token
        self.bot = telepot.Bot(self.token)
        self.callback_dict = {
            'chat': self.on_chat_message,
            'callback_query': self.callback_queries
        }
        self.client = MQTT(client_id, broker, port, self)
        self.chat_ids = []
        self.user_map = {}  # Maps user_id
        self.uv_threshold = 0
        self.uv_threshold_high = 5

    def start(self):
        MessageLoop(self.bot, self.callback_dict).run_as_thread()
        self.client.start()

    def load_config_from_catalog(self):
        try:
            response = requests.get("http://127.0.0.1:8080/config")
            if response.status_code == 200:
                config = response.json()
                self.uv_threshold = config.get("uv_threshold", 5)
                self.uv_threshold_high = self.uv_threshold + 4
                print(f"[CONFIG] UV threshold loaded: {self.uv_threshold}")
        except Exception as e:
            print(f"[CONFIG] Error: {e}")

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        if content_type == 'text':
            if msg['text'] == '/start':
                if chat_ID not in self.chat_ids:
                    self.chat_ids.append(chat_ID)
                    self.bot.sendMessage(chat_ID, "✅ You have successfully registered! You will now receive UV alerts.")
                    self.ask_location(chat_ID)
            elif msg['text'] == '/subscribe':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Start UV Monitoring', callback_data='full')]
                ])
                self.bot.sendMessage(chat_ID, 'Sunscreen Reminder', reply_markup=keyboard)
        elif content_type == "location":
            latitude = msg['location']['latitude']
            longitude = msg['location']['longitude']

            city = self.get_city_from_coords(lat = latitude, lon = longitude)
            data = {"city" : city}

            chat_id = msg['chat']['id']
            user_id = f"user{chat_id}"
            self.user_map[user_id] = chat_id

            # Publish city info to WeatherStack subscriber
            self.client.myPublish(f"UVAlert/{user_id}/location", data)
            self.bot.sendMessage(chat_ID, f"📍 Location received: {city}. UV monitoring will begin.")

        print(f"Content type: {content_type}, Chat type: {chat_type}, Chat ID: {chat_ID}")

    def ask_location(self, chat_ID):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📍 Share Location", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        self.bot.sendMessage(chat_ID, "Please share your location to start receiving UV alerts.", reply_markup=keyboard)

    def callback_queries(self, msg):
        query_id, ch_id, query = telepot.glance(msg, flavor='callback_query')

        if query == 'full':
            user_id = f"user{ch_id}"  # Use the same format you used earlier
            self.client.mySubscribe(f"UVAlert/{user_id}/#")
            # Subscribe to your specific MQTT topic
            self.bot.sendMessage(ch_id, '☀️ Started monitoring UV sensor data!')

    def notify(self, topic, payload):
        payload = json.loads(payload)
        print(f"Received payload: {payload}")

        try:
            user_id = topic.split("/")[1]
        except IndexError:
            return

        chat_id = self.user_map.get(user_id)
        if not chat_id:
            print(f"No chat_id found for user_id {user_id}")
            return
        if "uv" in payload:
            uv_level = payload.get('uv', 0)  # Extract 'uv' value from the MQTT payload
            if self.uv_threshold <= uv_level < self.uv_threshold_high:  # If UV level is dangerously high
                for chat_id in self.chat_ids:
                    self.bot.sendMessage(chat_id, f"⚠️ UV Index is high: {uv_level}!\nDon't forget to apply sunscreen! 🌞")
            elif uv_level >= self.uv_threshold_high:
                for chat_id in self.chat_ids:
                    self.bot.sendMessage(chat_id, f"⚠️ UV Index is really high: {uv_level}!\nDefinitely apply sunscreen, stay inside if you can! 🌞")
            elif uv_level < self.uv_threshold:
                for chat_id in self.chat_ids:
                    self.bot.sendMessage(chat_id, f"⚠️ UV Index is low: {uv_level}, you don't need sunscreen, at least for now!")
        elif "reminder" in payload:
            self.bot.sendMessage(chat_id, f"⏰ Re-apply your sunscreen now!")

    # Reverse geocode using OpenCage
    def get_city_from_coords(self, lat, lon):
        try:
            api_key = "875b673d64474f82b525facc7173a077"
            url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                components = data["results"][0]["components"]
                return components.get("city") or components.get("town") or components.get("village") or "Unknown"
        except Exception as e:
            print(f"[Geocoding] Error: {e}")
        return "Unknown"


if __name__ == '__main__':
    token = '8165914246:AAHJ8AuNe_rEd2NENCZmUI4ZfW5G3TB_xeg'
    broker = 'mqtt.eclipseprojects.io'
    port = 1883
    client_id = '6432360959'
    mybot = Mybot(token, client_id, broker, port)
    mybot.start()
    done = False
    while not done:
        time.sleep(5)
        done = True