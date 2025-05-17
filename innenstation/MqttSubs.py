#"Grund"code: https://tutorials-raspberrypi.de/datenaustausch-raspberry-pi-mqtt-broker-client/

import paho.mqtt.client as mqtt

MQTT_SERVER = "localhost"
MQTT_PATH   = "esp32/#"
 
def on_connect(client, userdata, flags, reasonCode, properties):
    print("Connected "+str(reasonCode))
    client.subscribe(MQTT_PATH)
 
def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")
    # more callbacks, etc
 
client = mqtt.Client(client_id="pi_innen", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect  = on_connect
client.on_message  = on_message
client.connect(MQTT_SERVER, 1883, 60)
client.loop_forever()