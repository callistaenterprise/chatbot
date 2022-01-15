package se.callistaenterprise.chadbot.services;

import org.springframework.stereotype.Service;
import se.callistaenterprise.chadbot.api.model.ChatResponse;
import se.callistaenterprise.chadbot.api.model.ResponseMessage;

import java.util.Arrays;
import java.util.List;

@Service
public class GreetingService implements ChatService {

    final private List<String> greetingResponses = Arrays.asList();

    public ChatResponse respond(String msg, String responseTo) {
        String goodbye = greetingResponses.stream()
                .skip(random.nextInt(greetingResponses.size()))
                .findFirst().get();
        return ChatResponse.builder()
                .id(responseTo)
                .message(ResponseMessage.builder()
                        .label(goodbye)
                        .build())
                .build();
    }
}
