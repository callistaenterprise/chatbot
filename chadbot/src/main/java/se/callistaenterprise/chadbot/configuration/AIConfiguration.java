package se.callistaenterprise.chadbot.configuration;

import org.datavec.api.records.reader.RecordReader;
import org.datavec.api.records.reader.impl.collection.CollectionSequenceRecordReader;
import org.deeplearning4j.nn.graph.ComputationGraph;
import org.deeplearning4j.nn.modelimport.keras.KerasModelImport;
import org.deeplearning4j.nn.modelimport.keras.exceptions.InvalidKerasConfigurationException;
import org.deeplearning4j.nn.modelimport.keras.exceptions.UnsupportedKerasConfigurationException;
import org.deeplearning4j.nn.modelimport.keras.preprocessing.text.KerasTokenizer;
import org.nd4j.linalg.dataset.api.iterator.MultiDataSetIterator;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;

import java.io.IOException;

@Configuration
public class AIConfiguration {

    @Bean
    public ComputationGraph sentimentClassifier() throws IOException, UnsupportedKerasConfigurationException, InvalidKerasConfigurationException {
        String sentimentAnalyserPath = new ClassPathResource("sentiment_classifier.h5").getPath();
        return KerasModelImport.importKerasModelAndWeights(sentimentAnalyserPath);
    }

    @Bean
    public KerasTokenizer tokenizer() throws IOException, InvalidKerasConfigurationException {
        String tokenizerPath = new ClassPathResource("tokenizer.json").getPath();
        return KerasTokenizer.fromJson(tokenizerPath);
    }

}
