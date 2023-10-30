// src/main/java/com/yourpackage/config/MQTTConfig.java

@Configuration
public class MQTTConfig {

    @Value("${mqtt.broker.url}")
    private String brokerUrl;

    @Value("${mqtt.client.id}")
    private String clientId;

    @Bean
    public MqttClient mqttClient() throws MqttException {
        MqttClient client = new MqttClient(brokerUrl, clientId);
        return client;
    }
}
