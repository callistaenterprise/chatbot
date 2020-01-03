package se.callistaenterprise.chatbot.datapreparer;

import lombok.Data;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Data
@Configuration
public class DataFilesConfiguration {

    @Value("${data.movies.metadata:}")
    private String movieMetadataFilePath;

    @Value("${data.movies.conversations:}")
    private String movieConversationFilePath;

    @Value("${data.convai:}")
    private String convaiConversationFilePath;

    @Value("${data.other:}")
    private String otherConversationFilePath;

    @Value("${vocabularis.lowerLimit:1}")
    private Integer wordCountLimit;
}
