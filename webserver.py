from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import paho.mqtt.client as mqtt
import threading
from multiprocessing import Pipe
import json 
from datetime import datetime


# MQTT configurations
BROKER_ADDRESS = "test.mosquitto.org"
RECEIVE_TOPIC = "test/receive_topic"
SEND_TOPIC = "test/send_topic"
RESPONSE_TOPIC = "test/response_topic"
INIT_TOPIC = "test/init_topic"


NODES = {}
TOPICS = [RECEIVE_TOPIC, INIT_TOPIC]

app = Flask(__name__, template_folder='./')
socketio = SocketIO(app)

# Create the SQLALCHEMY_DATABASE_URI using the provided dbConfig
db_user = 'dfrausto3@gatech.edu@boeingsqlserver'
db_password = 'blackhorse3!'
db_server = 'boeingsqlserver.database.windows.net'
db_name = 'boeingTestDatabase'

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mssql+pyodbc://{db_user}:{db_password}@{db_server}/{db_name}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)

db = SQLAlchemy(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    last_message_received = db.Column(db.DateTime)
    interval = db.Column(db.Integer)
    messages_count = db.Column(db.Integer)
    received_messages = db.Column(db.Integer)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    device = db.relationship('Device', backref=db.backref('temperature_data', lazy=True))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temp1 = db.Column(db.Float)
    temp2 = db.Column(db.Float)


# MQTT Receive callback
def on_message(client, userdata, message, pipe_end):
    topic = message.topic
    payload = message.payload.decode()

    if topic == INIT_TOPIC:
        node_id = json.loads(payload)["node_id"]
        location = json.loads(payload)["location"]
        NODES[node_id] = location
    else:
        print("TESTING")

    print(f"Received message: {payload} on topic {message.topic}")
    socketio.emit('new_message', {'message': payload})    

    # Send data to the main processing thread
    pipe_end.send((topic, payload))

# MQTT Receive Thread
def mqtt_receive_thread(pipe_end):
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS)
    
    for topic in TOPICS:
        client.subscribe(topic)
    
    client.on_message = lambda client, userdata, message: on_message(client, userdata, message, pipe_end)
    client.loop_forever()
    
# MQTT Send Thread
def mqtt_send_thread(pipe_end):
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS)
    while True:
        topic, message = pipe_end.recv()
        client.publish(RESPONSE_TOPIC, message)
        
def central_processing_thread(recv_from_flask, recv_from_mqtt, send_to_mqtt):
    while True:
        node_id, value1, value2 = recv_from_flask.recv()

        # Process the data (for now, we'll just format it as JSON)
        message_payload = json.dumps({
            "node_id": node_id,
            "value1": value1,
            "value2": value2
        })

        # Send the processed data to the MQTT send thread
        send_to_mqtt.send((SEND_TOPIC, message_payload))

@app.route('/')
def index():
    return render_template('index.html', nodes=NODES)

@app.route('/send_data', methods=['POST'])
def send_data():
    node_id = request.form['node_id']
    value1 = request.form['value1']
    value2 = request.form['value2']

    # Send data to the central processing thread
    flask_write.send((node_id, value1, value2))

    return jsonify(success=True, message=f"Data sent to {node_id}")

if __name__ == '__main__':
    # Create pipes
    read_central, central_write = Pipe(duplex=False)
    read_receive, receive_write = Pipe(duplex=False)
    read_flask, flask_write = Pipe(duplex=False)

    # Start Central Processing Thread
    threading.Thread(target=central_processing_thread, args=(read_flask, read_receive, central_write)).start()

    # Start MQTT Receive Thread
    threading.Thread(target=mqtt_receive_thread, args=(receive_write,)).start()

    # Start MQTT Send Thread
    threading.Thread(target=mqtt_send_thread, args=(read_central,)).start()

    # Start Flask Web Server
    socketio.run(app, port=8080)