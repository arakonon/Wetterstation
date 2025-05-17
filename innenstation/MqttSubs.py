#"Grund"code: https://tutorials-raspberrypi.de/datenaustausch-raspberry-pi-mqtt-broker-client/

import paho.mqtt.client as mqtt

MQTT_SERVER = "localhost"
MQTT_PATH   = "esp32/#"
 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")
    # more callbacks, etc
 
 
client = mqtt.Client("pi_innen")
client.on_connect  = on_connect
client.on_message  = on_message
client.connect(MQTT_SERVER, 1883, 60)
client.loop_forever()