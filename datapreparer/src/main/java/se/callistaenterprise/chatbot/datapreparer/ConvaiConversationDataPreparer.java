package se.callistaenterprise.chatbot.datapreparer;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.stream.Stream;

@Slf4j
@Component
@Order(2)
public class ConvaiConversationDataPreparer implements CommandLineRunner {

    @Autowired
    private DataFilesConfiguration configuration;

    @Override
    public void run(String... args) throws Exception {
        final String convaiConversationFilePath = configuration.getConvaiConversationFilePath();
        log.info("Reading conversational data from {}", convaiConversationFilePath);

        try (Stream<String> stream = Files.lines(Paths.get(convaiConversationFilePath))) {
            stream.forEach(System.out::println);
        } catch (IOException e) {
            log.error("Failed to read file {}", convaiConversationFilePath, e);
        }

    }
}
