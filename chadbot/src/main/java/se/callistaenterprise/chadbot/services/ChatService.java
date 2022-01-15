package se.callistaenterprise.chadbot.services;

import se.callistaenterprise.chadbot.api.model.ChatResponse;

import java.util.Random;

public interface ChatService {
    Random random = new Random();
    ChatResponse respond(String msg, String responseTo);
}
