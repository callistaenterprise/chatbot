package se.callistaenterprise.chadbot.api.model;

import lombok.Data;

@Data
public class ChatMessage {
    private String requestNumber;
    private String responseTo;
    private String value;
    private String botId;
    private String language;
}
