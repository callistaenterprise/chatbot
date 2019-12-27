package se.callistaenterprise.chatbot.datapreparer;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.function.BiFunction;
import java.util.function.BinaryOperator;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Slf4j
@Component
@Order(1)
public class MovieConversationDataPreparer  implements CommandLineRunner {

    @Autowired
    private DataFilesConfiguration configuration;

    @Override
    public void run(String... args) throws Exception {
        final String movieMetadataFilePath = configuration.getMovieMetadataFilePath();
        final String movieConversationFilePath = configuration.getMovieConversationFilePath();
        log.info("Reading conversational data from {}", movieConversationFilePath);
        final Map<String, String> questionsAndAnswers = new HashMap<>();
        final Map<String, String> conversationData = new HashMap<>();
        try (Stream<String> metadataStream = Files.lines(Paths.get(movieMetadataFilePath));
             Stream<String> conversationStream = Files.lines(Paths.get(movieConversationFilePath))) {
            // A Map as { {"L194" -> "L195"}, {"L195" -> "L196"}, {"L196" -> "L197"}} with conversation exchanges line codes
            final Map<String, String> conversations = metadataStream
                    .map(toConversationMetadata)
                    .map(Map::entrySet)
                    .flatMap(Collection::stream)
                    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

            // A Map as { {"L194" -> "It is a lovely day today!"}, {"L195" -> "Oh, you do not say!"} } with line codes to actual line
            conversationStream
                    .map(expand)
                    .map(toConversationLine)
                    .forEach(simpleEntry -> conversationData.put(simpleEntry.getKey(), simpleEntry.getValue()));
            // A Map as { {"It is a lovely day today!" -> "Oh, you do not say!"}, ... }
            conversations.entrySet().stream()
                    .map(entry -> new AbstractMap.SimpleEntry<String, String>(conversationData.get(entry.getKey()), conversationData.get(entry.getValue())))
                    .forEach(simpleEntry -> questionsAndAnswers.put(simpleEntry.getKey(), simpleEntry.getValue()));
        } catch (IOException e) {
            log.error("Failed to read file {}", movieConversationFilePath, e);
        }
        // Maps of all words (in lowercase) occurring in conversations with the number of occurrences
        final Map<String, Integer> wordCountQuestions = new HashMap<>();
        final Map<String, Integer> wordCountAnswers = new HashMap<>();
        // Tokenize "Questions" part
        questionsAndAnswers.keySet().stream()
                .map(String::toLowerCase)
                .map(str -> str.split(" "))
                .forEach(arr -> {
                    for (String s : arr) {
                        Integer wordCount = wordCountQuestions.containsKey(s) ? wordCountQuestions.get(s)+1 : 1;
                        wordCountQuestions.put(s, wordCount);
                    }
                });
        // Tokenize "Answers" part
        questionsAndAnswers.values().stream()
                .map(String::toLowerCase)
                .map(str -> str.split(" "))
                .forEach(arr -> {
                    for (String s : arr) {
                        Integer wordCount = wordCountAnswers.containsKey(s) ? wordCountAnswers.get(s)+1 : 1;
                        wordCountAnswers.put(s, wordCount);
                    }
                });
        final Integer maxNumberOfWordsInUtterance = conversationData.values().stream()
                .reduce(longestUtterance)
                .get().split(" ").length;
        final Integer lowerWordCountLimit = configuration.getWordCountLimit();
        // Words that should be replaced by filter-token from questions conversation-set
        final Set<String> questionWordsToReplace = wordCountQuestions.entrySet().stream()
                .filter(stringIntegerEntry -> stringIntegerEntry.getValue() >= lowerWordCountLimit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());
        final Set<String> answerWordsToReplace = wordCountAnswers.entrySet().stream()
                .filter(stringIntegerEntry -> stringIntegerEntry.getValue() >= lowerWordCountLimit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());
        // Filter and pad
        final Map<String, String> paddedAndFilteredQuestionsAndAnswers = questionsAndAnswers.entrySet().stream()
                .map(entry -> {
                    String q = entry.getKey();
                    String a = entry.getValue();
                    String[] qArr = new String[maxNumberOfWordsInUtterance+2];
                    String[] aArr = new String[maxNumberOfWordsInUtterance+2];
                    qArr[0] = "<SOS>";
                    aArr[0] = "<SOS>";
                    qArr[qArr.length-1] = "<EOS>";
                    aArr[aArr.length-1] = "<EOS>";
                    int i = 1;
                    for (String t : q.split(" ")) {
                        t = questionWordsToReplace.contains(t.toLowerCase()) ? "<OUT>" : t;
                        qArr[i++] = t;
                    }
                    for (; i < qArr.length-1; i++) {
                        qArr[i] = "<PAD>";
                    }
                    i = 1;
                    for (String t : a.split(" ")) {
                        t = answerWordsToReplace.contains(t.toLowerCase()) ? "<OUT>" : t;
                        aArr[i++] = t;
                    }
                    for (; i < aArr.length-1; i++) {
                        aArr[i] = "<PAD>";
                    }
                    return new AbstractMap.SimpleEntry<String, String>(String.join(" ", qArr), String.join(" ", aArr));
                })
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

        /*
        Files.write(
      Paths.get(fileName),
      contentToAppend.getBytes(),
      StandardOpenOption.APPEND);
        * */
       // Files.write(Paths.get("/tmp/questions.txt"), , )
    }

    // convert a conversation definition into a map of prev and next utterances
    private Function<String, Map<String, String>> toConversationMetadata = s -> {
        // E.g. u0 +++$+++ u2 +++$+++ m0 +++$+++ ['L194', 'L195', 'L196', 'L197'] => 'L194', 'L195', 'L196', 'L197'
        final String conversationLines = s.substring(s.indexOf('['), s.indexOf(']'));
        // E.g. L194 L195 L196 L197 (as array)
        final String[] individualConversationLines = conversationLines.replace("'", "").split(",");
        Map<String, String> prev2next = new HashMap<>();
        for (int i=0; i<individualConversationLines.length; i++) {
            String prevLineId = individualConversationLines[i].trim();
            if (individualConversationLines.length > i) {
                prev2next.put(prevLineId, individualConversationLines[i+1].trim());
            }
        }
        // For example above, should return a Map as { {"L194" -> "L195"}, {"L195" -> "L196"}, {"L196" -> "L197"}}
        return prev2next;
    };

    // Transform e.g. L194 +++g+++ u12 +++g+++ m1 +++g+++ STEVEN +++g+++ It is a lovely day today! to a Map.Entry of {"L194" -> "It is a lovely day today!"}
    private Function<String, Map.Entry<String, String>> toConversationLine = s -> {
        final String[] segments = s.split(" ");
        if (segments.length > 9) {
            segments[8] = String.join("", Arrays.copyOfRange(segments, 8, segments.length));
        }
        return new AbstractMap.SimpleEntry(segments[0], segments[8]);
    };

    private Function<String, String> expand = s -> {
        String str = s.replace("'m", " am");
        str = str.replace("e's", "e is");
        str = str.replace("t's", "t is");
        str = str.replace("'ll", " will");
        str = str.replace("'ve", " have");
        str = str.replace("'re", " are");
        str = str.replace("'d", " would");
        str = str.replace("on't", "ill not");
        str = str.replace("an't", "annot");
        str = str.replace("[-()\"#@/;:<>{}+=~|.?,]", "");
        return str;
    };

    private BinaryOperator<String> longestUtterance = (s1, s2) -> s1.split(" ").length > s2.split(" ").length ? s1 : s2;


    @Data
    private static class Conversation {
        String movieId;
        List<String> lines;
    }

}
