package se.callistaenterprise.chadbot.services;

import org.springframework.stereotype.Service;
import se.callistaenterprise.chadbot.api.model.ChatResponse;
import se.callistaenterprise.chadbot.api.model.ResponseMessage;

import java.util.Arrays;
import java.util.List;

@Service
public class SuggesionService implements ChatService {

    final private List<String> suggestionResponses = Arrays.asList();

    public ChatResponse respond(String cleanedMsg, String responseTo) {
        String goodbye = suggestionResponses.stream()
                .skip(random.nextInt(suggestionResponses.size()))
                .findFirst().get();
        return ChatResponse.builder()
                .id(responseTo)
                .message(ResponseMessage.builder()
                        .label(goodbye)
                        .build())
                .build();
    }
}
