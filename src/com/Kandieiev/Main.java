package com.Kandieiev;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Array;
import java.util.*;

public class Main {

    public static void main(String[] args) throws IOException {
        String text = readFile("short.txt");
        text = text.toLowerCase(Locale.ROOT);
        text = text.replaceAll("[^A-Za-z ]", "");
        text = deleteWords("skip_words.txt", text);
        System.out.println(text);

        CountMinSketch cms = new CountMinSketch();

        Arrays.stream(text.split(" ")).forEach(e -> cms.insert(e.hashCode()));
        cms.table();
        System.out.println("Min = " + cms.sketchCount("adventure".hashCode()));
    }

    public static String readFile(String path) throws IOException {
        return new String(Files.readAllBytes(Paths.get(path)));
    }

    public static String deleteWords(String path, String text) throws IOException{
        String words = readFile(path);
        String [] temp = words.split("\n");
        List<String> banWord = Arrays.asList(temp);

        for (String word: banWord) {
            word = word.replaceAll("[^A-Za-z ]", "");
            word = word + " ";
            text = text.replaceAll(word, "");
        }
        return text;
    }
}
