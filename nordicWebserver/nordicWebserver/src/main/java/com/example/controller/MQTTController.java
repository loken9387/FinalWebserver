// src/main/java/com/yourpackage/controller/MQTTController.java

@RestController
@RequestMapping("/mqtt")
public class MQTTController {

    @Autowired
    private MQTTSenderService mqttSenderService;

    @PostMapping("/send")
    public ResponseEntity<String> sendMessage(@RequestBody String messageContent) {
        mqttSenderService.sendMessage(messageContent);
        return ResponseEntity.ok("Message sent!");
    }
}
