import paho.mqtt.client as mqtt
import time
import json
import random

from webserver import RECEIVE_TOPIC


BROKER_ADDRESS = "test.mosquitto.org"
SEND_TOPIC = "test/receive_topic"
RESPONSE_TOPIC = "test/response_topic"
INIT_TOPIC = "test/init_topic"
NODE_ID = "node_12345"

def on_message(client, userdata, message):
    print(f"Received response: {message.payload.decode()}")

client = mqtt.Client()
client.connect(BROKER_ADDRESS)
client.on_message = on_message

# Subscribe to RESPONSE_TOPIC
client.subscribe(RESPONSE_TOPIC)

# Send init message
# Mock data for Device
device_data = {
    "name": "MockDevice",
    "location": "MockLocation",
    "interval": random.randint(5, 15),
    "messages_count": 0,
    "received_messages": 0
}

client.publish(INIT_TOPIC, json.dumps(device_data), retain=False)
tmp = random.randint(123456, 123456789)
print(f"Sent init message with ID: {tmp}")

while True:
    # Mock data
    temperature_data = {
        "device_id": "MockDeviceID",
        "temp1": random.uniform(20.0, 30.0),
        "temp2": random.uniform(20.0, 30.0)
    }
    
    client.publish(RECEIVE_TOPIC, json.dumps(temperature_data), retain=False)
    print(f"Sent data: {temperature_data}")

    # Listen for a short duration to get the response
    client.loop(timeout=1.0)

    time.sleep(5)  # Send data every 5 seconds
