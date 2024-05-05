package com.amazonaws.tasks;

import java.io.File;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class LoadData {
    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        Table table = dynamoDB.getTable("Music");

        JsonParser parser = new JsonFactory().createParser(new File("a1.json"));

        JsonNode rootNode = new ObjectMapper().readTree(parser);

        JsonNode movies = rootNode.get("songs");

        for(JsonNode movie : movies) {

            String title = movie.path("title").asText();
            String artist = movie.path("artist").asText();

            try {
                table.putItem(new Item()
                        .withPrimaryKey("title", title, "artist", artist)
                        .withJSON("release_year", movie.get("year").toString())
                        .withJSON("web_url", movie.get("web_url").toString())
                        .withJSON("image_url", movie.get("img_url").toString()));

                System.out.println("Music added: " + title + " by " + artist);

            }
            catch (Exception e) {
                System.err.println("Unable to add music: " + title + " by " + artist);
                System.err.println(e.getMessage());
                break;
            }
        }
        parser.close();
    }
}
