// src/main/java/com/yourpackage/service/MQTTSenderService.java

@Service
public class MQTTSenderService {

    @Autowired
    private MqttClient mqttClient;

    private final String topic = "your/send/topic";

    public void sendMessage(String messageContent) {
        try {
            if (!mqttClient.isConnected()) {
                mqttClient.connect();
            }
            MqttMessage message = new MqttMessage(messageContent.getBytes());
            mqttClient.publish(topic, message);
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
}
