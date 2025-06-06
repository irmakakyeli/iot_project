import paho.mqtt.client as mqtt
import json


class MQTT:
    def __init__(self, clientID, broker, port, notifier=None):
        self.broker = "mqtt.eclipseprojects.io" 
        self.port = 1883 
        self.clientID = clientID
        self._topic = " "
        self._isSubscriber = False
        self.notifier = notifier #change
    

        #create an instance of paho.mqtt.client
        self._paho_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, clientID)
        #register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))
    
    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        #new message is received
        self.notifier.notify(msg.topic, msg.payload)
    
    def myPublish (self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)

    def mySubscribe(self, topic):

        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)
        # it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic
        print("Subscribed to %s" % (topic))

    def start(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker , self.port)
        self._paho_mqtt.loop_start()
    
    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
    def stop (self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
       
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
















