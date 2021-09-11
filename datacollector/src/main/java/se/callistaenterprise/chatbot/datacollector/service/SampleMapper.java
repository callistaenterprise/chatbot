package se.callistaenterprise.chatbot.datacollector.service;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.factory.Mappers;
import reactor.core.publisher.Mono;
import se.callistaenterprise.chatbot.datacollector.api.Sample;
import se.callistaenterprise.chatbot.datacollector.data.SampleEntity;

@Mapper
public interface SampleMapper {

    SampleMapper INSTANCE = Mappers.getMapper(SampleMapper.class);

    @Mapping(source = "id", target = "sampleId")
    Sample toSample(SampleEntity sampleEntity);

    @Mapping(source = "sampleId", target = "id")
    SampleEntity toSampleEntity(Sample sample);

    default Mono<SampleEntity> fromMonoSample(Mono<Sample> sample) {
        return sample.map(this::toSampleEntity);
    }

    default Mono<Sample> fromMonoSampleEntity(Mono<SampleEntity> sampleEntity) {
        return sampleEntity.map(this::toSample);
    }

}
