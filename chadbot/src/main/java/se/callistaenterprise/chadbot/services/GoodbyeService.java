package se.callistaenterprise.chadbot.services;

import org.springframework.stereotype.Service;
import se.callistaenterprise.chadbot.api.model.ChatResponse;
import se.callistaenterprise.chadbot.api.model.ResponseMessage;

import java.util.Arrays;
import java.util.List;

@Service
public class GoodbyeService implements ChatService {

    private static final List<String> goodbyeMessages = Arrays.asList();

    public ChatResponse respond(String cleanedMsg, String responseTo) {
        String goodbye = goodbyeMessages.stream()
                .skip(random.nextInt(goodbyeMessages.size()))
                .findFirst().get();
        return ChatResponse.builder()
                .id(responseTo)
                .message(ResponseMessage.builder()
                        .label(goodbye)
                        .build())
                .build();
    }
}
