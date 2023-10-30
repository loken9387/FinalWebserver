// src/main/java/com/yourpackage/service/MQTTReceiverService.java

@Service
public class MQTTReceiverService implements Runnable {

    @Autowired
    private MqttClient mqttClient;

    private final String topic = "your/receive/topic";

    @PostConstruct
    public void init() {
        new Thread(this).start();
    }

    @Override
    public void run() {
        try {
            mqttClient.setCallback(new MqttCallback() {
                @Override
                public void connectionLost(Throwable cause) {
                    // Handle connection lost
                }

                @Override
                public void messageArrived(String topic, MqttMessage message) throws Exception {
                    // Handle received message
                    System.out.println("Received message: " + new String(message.getPayload()));
                }

                @Override
                public void deliveryComplete(IMqttDeliveryToken token) {
                    // Handle delivery complete
                }
            });

            mqttClient.connect();
            mqttClient.subscribe(topic);

        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
}
