package se.callistaenterprise.chatbot.datacollector.api;

import lombok.Data;

import java.util.UUID;

@Data
public class Sample {
    private String contextWords, centerWord;
    private UUID sampleId;
}
