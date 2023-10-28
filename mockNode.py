import paho.mqtt.client as mqtt
import time
import json

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
init_payload = json.dumps({"node_id": NODE_ID, "location": "poop"})
client.publish(INIT_TOPIC, init_payload, retain=False)
print(f"Sent init message with ID: {NODE_ID}")

while True:
    # Mock data
    payload = json.dumps({"temperature": 23.4, "humidity": 56.7})
    client.publish(SEND_TOPIC, payload, retain=False)
    print(f"Sent data: {payload}")

    # Listen for a short duration to get the response
    client.loop(timeout=1.0)

    time.sleep(5)  # Send data every 5 seconds
