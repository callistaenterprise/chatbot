package se.callistaenterprise.chadbot.services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import se.callistaenterprise.chadbot.api.model.BlogLink;
import se.callistaenterprise.chadbot.api.model.ChatResponse;
import se.callistaenterprise.chadbot.api.model.ResponseMessage;

import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
public class RequestService implements ChatService {

    @Autowired
    private BlogFinderService blogFinderService;
    private static final DateTimeFormatter DATE_TIME_FORMATTER = DateTimeFormatter.ISO_DATE;

    // TODO: it is here the hard work really kicks in!
    public ChatResponse respond(String cleanedMsg, String responseTo) {
        final Set<BlogLink> urls = Stream.of(cleanedMsg.split(" "))
                .filter(removeStopWords)
                .map(blogFinderService::findNearestBlogs)
                .flatMap(List::stream)
                .collect(Collectors.toSet());

        final ChatResponse response = ChatResponse.builder()
                .id(responseTo)
                .message(ResponseMessage.builder()
                        .label(String.format("Here you are, I found %d links that might interest you", urls.size()))
                        .build())
                .build();
        urls.stream()
                .sorted()
                .map(url -> ResponseMessage.builder()
                        .label("")
                        .link(url.getLink())
                        .publishedDate(url.getPublishedDate().format(DATE_TIME_FORMATTER))
                        .build())
                .collect(Collectors.toCollection(() -> response.getMessages()));
        return response;
    }

    Predicate<String> removeStopWords = s ->
            !Arrays.asList("a", "about", "afternoon", "am", "and", "any", "anything", "are",
                    "away", "awesome", "beautiful", "blog", "blogs", "bye", "can", "cheerio",
                    "cheers", "day", "dislike", "do", "else", "evening", "find", "for", "friend",
                    "get", "give", "going", "good", "goodbye", "goodnight", "great", "greeting",
                    "greetings", "have", "hello", "helpful", "hey", "hi", "hiya", "how", "howdy",
                    "i", "in", "interested", "is", "it", "later", "like", "liked", "link", "looking",
                    "lot", "me", "morning", "much", "my", "no", "now", "of", "ok", "on", "other",
                    "please", "question", "read", "really", "regarding", "related", "request", "searching",
                    "see", "show", "similar", "something", "suggestion", "super", "talk", "tell", "thank",
                    "thanks", "that", "there", "them", "they", "things", "this", "to", "up", "very", "was",
                    "what", "where", "ya", "you").contains(s);
}
