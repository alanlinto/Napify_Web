package com.amazonaws.tasks;

//imports for Dynamo DB
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.*;

//imports for S3 bucket
import com.amazonaws.AmazonServiceException;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;

//Imports for Image Downloading
import java.awt.Image;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import javax.imageio.ImageIO;

import java.util.Iterator;

public class RetrieveImages {

    private final static String downloaded_image = "download.jpg";

    private static void downloadImage(String image_url, String artist) throws IOException{

            URL image_from_url = new URL(image_url);
            Image image = ImageIO.read(image_from_url);

            File outputFile = new File(downloaded_image);
            ImageIO.write(toBufferedImage(image), "jpg", outputFile);
    }

    private static BufferedImage toBufferedImage(Image img) {

        BufferedImage b_image = new BufferedImage(img.getWidth(null), img.getHeight(null), BufferedImage.TYPE_INT_RGB);
        b_image.getGraphics().drawImage(img, 0, 0, null);

        return b_image;
    }

    public static void uploadImage(AmazonS3 s3Client, String file, String filename) throws AmazonServiceException{

        String bucketName = "a1-task2-s3806891"; //The S3 bucket using for this assignment.
        PutObjectRequest request = new PutObjectRequest(bucketName, filename, new File(file));
        ObjectMetadata metadata = new ObjectMetadata();
        metadata.setContentType("plain/text");
        metadata.addUserMetadata("title", "someTitle");
        request.setMetadata(metadata);
        s3Client.putObject(request);

    }

    public static void main(String[] args) {

        AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .build();

        AmazonDynamoDB dbClient = AmazonDynamoDBClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(dbClient);

        Table table = dynamoDB.getTable("Music");

        ItemCollection<ScanOutcome> scanner = table.scan();
        Iterator<Item> iterator = scanner.iterator();


        while (iterator.hasNext()) {
            Item item = iterator.next();
            try {
                String artist = item.getString("Artist");
                String image_url = item.getString("image_url");
                String filename = artist + ".jpg";
                RetrieveImages.downloadImage(image_url, artist);
                System.out.println("Download Image of artist: " + artist);
                RetrieveImages.uploadImage(s3Client, downloaded_image, filename);
                System.out.println("Uploaded Image of artist: " + artist + " to the S3 bucket");
            }
            catch(IOException e){
                System.err.println("Unable to download artist image : Operation Failed !!!!");
                break;
            }
            catch(AmazonServiceException e){
                System.err.println("Unable to upload artist image : Operation Failed !!!!");
                break;
            }
            catch(Exception e) {
                System.err.println("Unable to retrieve artist image url : Operation Failed !!!!");
                break;
            }
        }
    }
}
