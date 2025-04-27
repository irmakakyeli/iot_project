import telepot
from telepot.loop import MessageLoop
import time
import MQTT  # Make sure you have an MQTT.py file
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json

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

    def start(self):
        MessageLoop(self.bot, self.callback_dict).run_as_thread()
        self.client.start()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        if content_type == 'text':
            if msg['text'] == '/start':
                if chat_ID not in self.chat_ids:
                    self.chat_ids.append(chat_ID)
                    self.bot.sendMessage(chat_ID, "✅ You have successfully registered! You will now receive UV alerts.")
            elif msg['text'] == '/subscribe':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Start UV Monitoring', callback_data='full')]
                ])
                self.bot.sendMessage(chat_ID, 'Sunscreen Reminder', reply_markup=keyboard)

        print(f"Content type: {content_type}, Chat type: {chat_type}, Chat ID: {chat_ID}")

    def callback_queries(self, msg):
        query_id, ch_id, query = telepot.glance(msg, flavor='callback_query')

        if query == 'full':
            # Subscribe to your specific MQTT topic
            self.client.mySubscribe('UVAlert/1/#')
            self.bot.sendMessage(ch_id, '☀️ Started monitoring UV sensor data!')

    def notify(self, topic, payload):
        payload = json.loads(payload)
        print(f"Received payload: {payload}")
        
        uv_level = payload.get('uv', 0)  # Extract 'uv' value from the MQTT payload
        if uv_level >= 7:  # If UV level is dangerously high
            for chat_id in self.chat_ids:
                self.bot.sendMessage(chat_id, f"⚠️ UV Index is very high: {uv_level}!\nDon't forget to apply sunscreen! 🌞")

if __name__ == '__main__':
    token = '8165914246:AAHJ8AuNe_rEd2NENCZmUI4ZfW5G3TB_xeg'
    broker = 'mqtt.eclipseprojects.io'
    port = 1883
    client_id = '6432360959'
    mybot = Mybot(token, client_id, broker, port)
    mybot.start()

    while True:
        time.sleep(5)