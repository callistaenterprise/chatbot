package se.callistaenterprise.chadbot.api;

import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import se.callistaenterprise.chadbot.api.model.ChatMessage;
import se.callistaenterprise.chadbot.api.model.ChatResponse;
import se.callistaenterprise.chadbot.services.*;

import static se.callistaenterprise.chadbot.services.MessageCleanerService.clean;

@AllArgsConstructor
@RestController
@RequestMapping("/api/chat")
public class ChatApi {

    private SentimentAnalyserService sentimentAnalyserService;
    private GreetingService greetingService;
    private RequestService requestService;
    private GoodbyeService goodbyeService;
    private ThanksService thanksService;
    private DislikeService dislikeService;
    private SuggesionService suggestionService;
    private UnknownSentimentService unknownSentimentService;

    @PostMapping(produces = "application/json")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatMessage msg) {
        String cleanedMsg = clean.apply(msg.getValue());
        final Sentiment sentiment = sentimentAnalyserService.determineSentiment(cleanedMsg);
        switch (sentiment) {
            case Greeting:
                return ResponseEntity.ok(greetingService.respond(cleanedMsg, msg.getResponseTo()));
            case Request:
                return ResponseEntity.ok(requestService.respond(cleanedMsg, msg.getResponseTo()));
            case Goodbye:
                return ResponseEntity.ok(goodbyeService.respond(cleanedMsg, msg.getResponseTo()));
            case Thanks:
                return ResponseEntity.ok(thanksService.respond(cleanedMsg, msg.getResponseTo()));
            case Dislike:
                return ResponseEntity.ok(dislikeService.respond(cleanedMsg, msg.getResponseTo()));
            case Suggestion:
                return ResponseEntity.ok(suggestionService.respond(cleanedMsg, msg.getResponseTo()));
            default:
                return ResponseEntity.ok(unknownSentimentService.respond(cleanedMsg, msg.getResponseTo()));
        }
    }
}
