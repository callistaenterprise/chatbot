package se.callistaenterprise.chadbot.api.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ResponseMessage {
    private String label;
    private String link;
    @JsonProperty("linkcategory")
    private String linkCategory;
    @JsonProperty("publisheddate")
    private String publishedDate;
    private final String objectVersion = "1.0";

}
