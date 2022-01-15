package se.callistaenterprise.chadbot.api.model;

import lombok.Builder;
import lombok.Data;
import lombok.Singular;

import java.util.List;

@Data
@Builder
public class ChatResponse {
    private final String action = "chat";
    private String id;
    @Singular
    private List<ResponseMessage> messages;
    private final String objectVersion = "1.0";
    @Singular
    private List<ResponseMessage> teasers;
}
