package se.callistaenterprise.chatbot.datapreparer;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.function.BinaryOperator;
import java.util.function.Function;
import java.util.stream.Collectors;

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
        try (BufferedReader metadataReader = new BufferedReader(new InputStreamReader(new FileInputStream(movieMetadataFilePath), StandardCharsets.UTF_8));
             BufferedReader conversationReader = new BufferedReader(new InputStreamReader(new FileInputStream(movieConversationFilePath), StandardCharsets.UTF_8))) {
            // A Map as { {"L194" -> "L195"}, {"L195" -> "L196"}, {"L196" -> "L197"}} with conversation exchanges line codes
            final Map<String, String> conversations = metadataReader.lines()
                    .map(toConversationMetadata)
                    .map(Map::entrySet)
                    .flatMap(Collection::stream)
                    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

            // A Map as { {"L194" -> "It is a lovely day today!"}, {"L195" -> "Oh, you do not say!"} } with line codes to actual line
            conversationReader.lines()
                    .map(toConversationLine)
                    .forEach(simpleEntry -> {
                        conversationData.put(simpleEntry.getKey(), expand.apply(simpleEntry.getValue()));
                    });
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
        // Count number of occurrences for each word used as question.
        questionsAndAnswers.keySet().stream()
                .map(String::toLowerCase)
                .map(str -> str.split(" "))
                .forEach(arr -> {
                    if (arr.length > 0) {
                        for (String s : arr) {
                            Integer wordCount = wordCountQuestions.containsKey(s) ? wordCountQuestions.get(s) + 1 : 1;
                            wordCountQuestions.put(s, wordCount);
                        }
                    }
                });
        // Count number of occurrences for each word used as answer.
        questionsAndAnswers.values().stream()
                .map(String::toLowerCase)
                .map(str -> str.split(" "))
                .forEach(arr -> {
                    if (arr.length > 0) {
                        for (String s : arr) {
                            Integer wordCount = wordCountAnswers.containsKey(s) ? wordCountAnswers.get(s) + 1 : 1;
                            wordCountAnswers.put(s, wordCount);
                        }
                    }
                });
        final String[] longestSentence = conversationData.values().stream()
                .reduce(longestUtterance)
                .get().split(" ");
        log.info("LONGEST SENTENCE: {}", String.join(" ", longestSentence));
        final int maxNumberOfWordsInUtterance = longestSentence.length;
        log.info("Longest utterance used in body of text: {}", maxNumberOfWordsInUtterance);
        final Integer lowerWordCountLimit = configuration.getWordCountLimit();
        // Words that should be replaced by filter-token from questions conversation-set
        final Set<String> questionWordsToReplace = wordCountQuestions.entrySet().stream()
                .filter(stringIntegerEntry -> stringIntegerEntry.getValue() < lowerWordCountLimit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());
        final Set<String> answerWordsToReplace = wordCountAnswers.entrySet().stream()
                .filter(stringIntegerEntry -> stringIntegerEntry.getValue() < lowerWordCountLimit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());
        log.info("Words in 'questions' that will be replaced by <OUT>-token: {}", questionWordsToReplace);
        log.info("Words in 'answers' that will be replaced by <OUT>-token: {}", answerWordsToReplace);
        try (FileOutputStream prev = new FileOutputStream("/tmp/prev.txt");
             FileOutputStream next = new FileOutputStream("/tmp/next.txt")) {
            for (Map.Entry<String, String> qAndA : questionsAndAnswers.entrySet()) {
                String[] q = qAndA.getKey().split(" ");
                String[] a = qAndA.getValue().split(" ");
                StringBuilder qBuilder = new StringBuilder("<SOS> ");
                StringBuilder aBuilder = new StringBuilder("<SOS> ");
                for (int i=0; i<maxNumberOfWordsInUtterance; i++) {
                    if (i<q.length) {
                        qBuilder.append(questionWordsToReplace.contains(q[i]) ? "<OUT>" : q[i]);
                    } else {
                        qBuilder.append("<PAD>");
                    }
                    qBuilder.append(" ");
                    if (i<a.length) {
                        aBuilder.append(answerWordsToReplace.contains(a[i]) ? "<OUT>" : a[i]);
                    } else {
                        aBuilder.append("<PAD>");
                    }
                    aBuilder.append(" ");
                }
                String question = qBuilder.toString() + System.lineSeparator();
                String answer = aBuilder.toString() + System.lineSeparator();
                prev.write(question.getBytes());
                next.write(answer.getBytes());
            }
        } catch (IOException ioe) {
            log.error("Failed to write to output file.", ioe);
        }
    }

    // convert a conversation definition into a map of prev and next utterances
    private Function<String, Map<String, String>> toConversationMetadata = s -> {
        // E.g. u0 +++$+++ u2 +++$+++ m0 +++$+++ ['L194', 'L195', 'L196', 'L197'] => 'L194', 'L195', 'L196', 'L197'
        final String conversationLines = s.substring(s.indexOf('[')+1, s.indexOf(']'));
        // E.g. L194 L195 L196 L197 (as array)
        final String[] individualConversationLines = conversationLines.replace("'", "").split(",");
        Map<String, String> prev2next = new HashMap<>();
        for (int i=0; i<individualConversationLines.length-1; i++) {
            String prevLineId = individualConversationLines[i].trim();
            if (individualConversationLines.length-1 > i) {
                prev2next.put(prevLineId, individualConversationLines[i+1].trim());
            }
        }
        // For example above, should return a Map as { {"L194" -> "L195"}, {"L195" -> "L196"}, {"L196" -> "L197"}}
        return prev2next;
    };

    // Transform e.g. L194 +++g+++ u12 +++g+++ m1 +++g+++ STEVEN +++g+++ It is a lovely day today! to a Map.Entry of {"L194" -> "It is a lovely day today!"}
    private Function<String, Map.Entry<String, String>> toConversationLine = s -> {
        final String[] segments = s.split(" ");
        // Cleaning, sometimes the actual "line" doesn't start at index 8, so we go backwards to find from where to pick up the conversational line
        int start = segments.length-1;
        for (; start > 0; start--) {
            if (segments[start].equals("+++$+++")) {
                start++;
                break;
            }
        }
        if (segments.length > 8 && start > 0) {
            segments[8] = String.join(" ", Arrays.copyOfRange(segments, start, segments.length));
            return new AbstractMap.SimpleEntry(segments[0], segments[8]);
        }
        return new AbstractMap.SimpleEntry(segments[0], "");
    };

    private Function<String, String> expand = s -> {
        String str = s.replace("'m", " am");
        str = str.replace("'s", " is");
        str = str.replace("'ll", " will");
        str = str.replace("´ll", " will");
        str = str.replace("'ve", " have");
        str = str.replace("´ve", " have");
        str = str.replace("'re", " are");
        str = str.replace("´re", " are");
        str = str.replace("'d", " would");
        str = str.replace("´d", " would");
        str = str.replace("won't", "will not");
        str = str.replace("won´t", "will not");
        str = str.replace("don't", "do not");
        str = str.replace("don´t", "do not");
        str = str.replace("an't", "annot");
        str = str.replace("an´t", "annot");
        str = str.replace("*", "");
        str = str.replace("[", "");
        str = str.replace("]", "");
        str = str.replaceAll("\\t", " ");
        str = str.replaceAll("\\d", "number");
        str = str.replaceAll("[()\"#@/;:<>{}+=~|.!?,]", "");
        return str;
    };

    private BinaryOperator<String> longestUtterance = (s1, s2) -> s1.split(" ").length > s2.split(" ").length ? s1 : s2;

    private Function<String, Optional<String>> validateHasText = s -> {
        String str = s.replace(" ", "");
        str = str.replace("<SOS>", "");
        str = str.replace("<OUT>", "");
        str = str.replace("<PAD>", "");
        str = str.replace("<EOS>", "");
        return str.length() > 0 ? Optional.of(str) : Optional.empty();
    };

    @Data
    private static class Conversation {
        String movieId;
        List<String> lines;
    }

}
