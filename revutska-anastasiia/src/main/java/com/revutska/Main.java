package com.revutska;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import static java.lang.Math.abs;

public class Main {
    public static void main(String[] args) throws IOException {
        String inputPath = System.getProperty("input", "input_datasets.txt");
        int kNumber = Integer.parseInt(System.getProperty("k", "8"));
        int mBufferSize = Integer.parseInt(System.getProperty("m", "200"));
        int pNumberOfHashFunctions = Integer.parseInt(System.getProperty("p", "8"));
        int cNumberOfBitsPerCounter = Integer.parseInt(System.getProperty("c", "12"));

        CountMinSketch singleCMK = new CountMinSketch(mBufferSize, pNumberOfHashFunctions, kNumber, cNumberOfBitsPerCounter);

        List<String> skipWords = readStringsFromResources("skip_words.txt").stream()
            .map(String::toLowerCase)
            .collect(Collectors.toList());

        List<String> dataset = readStringsFromResources(inputPath).stream()
            .flatMap(str -> Arrays.stream(str.split("[\\W\\d]")))
            .filter(str -> !str.isEmpty() && !skipWords.contains(str.toLowerCase()))
            .collect(Collectors.toList());

        // Single processing
        dataset.forEach(singleCMK::setString);
        System.out.println("Single:");
        printOutputInTable(singleCMK.getKTop(), dataset);

        // Parallel processing
        CountMinSketch parallelCMK = new CountMinSketch(mBufferSize, pNumberOfHashFunctions, kNumber, cNumberOfBitsPerCounter);
        for (List<String> batch : splitOnBatches(dataset, mBufferSize)) {
            CountMinSketch cmk = new CountMinSketch(mBufferSize, pNumberOfHashFunctions, kNumber, cNumberOfBitsPerCounter);
            batch.forEach(cmk::setString);
            parallelCMK.merge(cmk);
        }
        System.out.println("Parallel:");
        printOutputInTable(parallelCMK.getKTop(), dataset);

    }

    private static List<String> readStringsFromResources(String filename) throws IOException {
        ClassLoader classLoader = Main.class.getClassLoader();
        try (var inputStream = classLoader.getResourceAsStream(filename);
             var bufferedReader = new BufferedReader(new InputStreamReader(inputStream))) {
            return bufferedReader.lines().collect(Collectors.toList());
        }
    }

    private static List<List<String>> splitOnBatches(List<String> dataset, int batchSize) {
        List<List<String>> batches = new ArrayList<>();
        List<String> batch = new ArrayList<>();
        for (String data : dataset) {
            if (batch.size() == batchSize) {
                batches.add(batch);
                batch = new ArrayList<>();
            } else if (batch.size() < batchSize) {
                batch.add(data);
            }
        }
        return batches;
    }

    private static void printOutputInTable(List<Map.Entry<String, Integer>> kTop, List<String> dataset) {
        Map<String, Long> realOccurrencesOfStrings = dataset.stream()
            .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));

        System.out.format("|%20s|%11s|%11s|%8s|\n", "word", "freq_ref", "freq_approx", "error %");
        for (Map.Entry<String, Integer> k : kTop) {
            String word = k.getKey();
            long freqRef = realOccurrencesOfStrings.get(word);
            long freqApprox = k.getValue();
            float error = (100.0f * abs(freqApprox - freqRef)) / freqRef;
            System.out.format("|%20s|%11d|%11d|%8.2f|\n", word, freqRef, freqApprox, error);
        }
        System.out.println();
    }
}
