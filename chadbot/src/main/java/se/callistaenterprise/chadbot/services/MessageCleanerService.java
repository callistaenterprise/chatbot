package se.callistaenterprise.chadbot.services;

import java.util.function.Function;

public class MessageCleanerService {

    public static Function<String, String> clean = s ->
        s.toLowerCase()
                .replaceAll("\\t", " ")
                .replaceAll("\\s+", " ")
                .replaceAll("-[readmore]-", " ")
                .replaceAll("'m", " am")
                .replaceAll(" 'n ", " and ")
                .replaceAll("'s", " is")
                .replaceAll("´s", "") // genitive-s: ignore
                .replaceAll("isn't", "is not")
                .replaceAll("'ll", " will")
                .replaceAll("’ll", " will")
                .replaceAll("'ve", " have")
                .replaceAll("'re", " are")
                .replaceAll("'d", " would")
                .replaceAll("'em", "them")
                .replaceAll("'bout", "about")
                .replaceAll("aren't", "are not")
                .replaceAll("ain't", "am not")
                .replaceAll("can't", "cannot")
                .replaceAll("didn't", "did not")
                .replaceAll("doesn't", "does not")
                .replaceAll("doin'", "doing")
                .replaceAll("don't", "do not")
                .replaceAll("haven't", "have not")
                .replaceAll("hasn't", "has not")
                .replaceAll("let's", "let us")
                .replaceAll("musn’t", "must not")
                .replaceAll("wasn't", "was not")
                .replaceAll("weren't", "were not")
                .replaceAll("won't", "will not")
                .replaceAll("wouldn't", "would not")
                .replaceAll(" - ", " ")
                .replaceAll("[-+]?[0-9]+[,0-9]*(\\.[0-9]+)?", "");


}
