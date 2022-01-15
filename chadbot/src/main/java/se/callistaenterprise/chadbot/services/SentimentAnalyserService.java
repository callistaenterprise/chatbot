package se.callistaenterprise.chadbot.services;

import org.deeplearning4j.nn.graph.ComputationGraph;
import org.deeplearning4j.nn.modelimport.keras.preprocessing.text.KerasTokenizer;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.function.Function;

@Service
public class SentimentAnalyserService {

    @Autowired
    private ComputationGraph sentimentClassifier;

    @Autowired
    private KerasTokenizer tokenizer;

    public Sentiment determineSentiment(String cleanedMsg) {
        final Integer[][] wordIds = tokenizer.textsToSequences(new String[]{cleanedMsg});
        final int[][] bigrams = toBigrams.apply(wordIds);
        final int[][] trigrams = toTrigrams.apply(wordIds);
        final INDArray[] output = sentimentClassifier.output(false, Nd4j.create(bigrams), Nd4j.create(trigrams));
        // TODO: interpret output to select sentimnent
        return Sentiment.Greeting;
    }

    Function<Integer[][], int[][]> toBigrams = wordIds -> {
        return null;
    };

    Function<Integer[][], int[][]> toTrigrams = wordIds -> {
        return null;
    };
}
