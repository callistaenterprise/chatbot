package se.callistaenterprise.chadbot.api.model;

import lombok.Data;

import java.time.LocalDate;

@Data
public class BlogLink implements Comparable<BlogLink> {
    private String link;
    private LocalDate publishedDate;

    @Override
    public int compareTo(BlogLink other) {
        return this.publishedDate.compareTo(other.publishedDate);
    }
}
