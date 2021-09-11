package se.callistaenterprise.chatbot.datacollector.data;

import org.springframework.data.repository.reactive.ReactiveCrudRepository;

public interface SampleRepository extends ReactiveCrudRepository<SampleEntity, Long> {
}
