package se.callistaenterprise.chadbot.services;

import org.springframework.stereotype.Service;
import se.callistaenterprise.chadbot.api.model.ChatResponse;
import se.callistaenterprise.chadbot.api.model.ResponseMessage;

@Service
public class UnknownSentimentService implements ChatService {

    public ChatResponse respond(String cleanedMsg, String responseTo) {
        return ChatResponse.builder()
                .id(responseTo)
                .message(ResponseMessage.builder()
                        .label("I'm really sorry, I don't understand what you mean?")
                        .build())
                .build();
    }
}
