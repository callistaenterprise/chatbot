package se.callistaenterprise.chatbot.datacollector.api;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;
import se.callistaenterprise.chatbot.datacollector.service.DataCollectorService;

@RestController("/data")
public class DataCollectorApi {

    @Autowired
    private DataCollectorService service;

    @PostMapping(value = "", produces = "application/json")
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<Sample> createSample(@RequestBody Sample sample) {
        return service.saveSample(sample);
    }

    
}
