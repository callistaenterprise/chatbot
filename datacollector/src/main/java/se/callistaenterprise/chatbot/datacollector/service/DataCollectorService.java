package se.callistaenterprise.chatbot.datacollector.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
import se.callistaenterprise.chatbot.datacollector.api.Sample;
import se.callistaenterprise.chatbot.datacollector.data.SampleEntity;
import se.callistaenterprise.chatbot.datacollector.data.SampleRepository;

@Service
public class DataCollectorService {

    @Autowired
    private SampleRepository repository;

    public Mono<Sample> saveSample(Sample sample) {
        final SampleEntity sampleEntity = SampleMapper.INSTANCE.toSampleEntity(sample);
        return SampleMapper.INSTANCE.fromMonoSampleEntity(repository.save(sampleEntity));
    }
}
