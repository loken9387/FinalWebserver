// ... [Previous web server code]

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

@SpringBootApplication
public class NordicWebserverApplication {

    private static final String BROKER_URL = "tcp://localhost:1883";
    private static final String TOPIC_SEND = "webserver/send";
    private static final String TOPIC_RECEIVE = "webserver/receive";
    private static MqttClient mqttClient;

    public static void main(String[] args) {
        SpringApplication.run(NordicWebserverApplication.class, args);
    }

    @PostConstruct
    public void init() throws Exception {
        // Initialize MQTT client
        mqttClient = new MqttClient(BROKER_URL, MqttClient.generateClientId(), new MemoryPersistence());
        mqttClient.connect();

        // Start threads for sending and receiving MQTT messages
        new Thread(() -> {
            try {
                handleMQTTReceiving();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();

        new Thread(() -> {
            try {
                handleMQTTSending();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

    @PreDestroy
    public void cleanup() throws MqttException {
        if (mqttClient != null && mqttClient.isConnected()) {
            mqttClient.disconnect();
        }
    }

    private static void handleMQTTReceiving() throws MqttException {
        mqttClient.subscribe(TOPIC_RECEIVE);
        mqttClient.setCallback(new MqttCallback() {
            @Override
            public void connectionLost(Throwable cause) {
                // Handle connection loss
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                // Handle received messages
                System.out.println("Received message: " + new String(message.getPayload()));
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
                // Handle delivery confirmation
            }
        });
    }

    private static void handleMQTTSending() throws MqttException, InterruptedException {
        while (true) {
            // Send a message every 10 seconds for demonstration purposes
            MqttMessage message = new MqttMessage("Hello from web server!".getBytes());
            mqttClient.publish(TOPIC_SEND, message);
            Thread.sleep(10000);
        }
    }
}

@RestController
class WebController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello from Spring Boot!";
    }
}
