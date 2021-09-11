package se.callistaenterprise.chatbot.datacollector.data;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

import java.util.UUID;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Table("sample")
public class SampleEntity {

    @Id
    private UUID id;

    @Column("context_words")
    private String contextWords;

    @Column("center_word")
    private String centerWord;
}
