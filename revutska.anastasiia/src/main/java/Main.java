import jdk.dynalink.linker.LinkerServices;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) throws IOException {
        CountMinSketch singleCMK = new CountMinSketch(200, 8, 8);

        List<String> skipWords = readStringsFromResources("skip_words.txt").stream()
            .map(String::toLowerCase)
            .collect(Collectors.toList());

        List<String> dataset =  readStringsFromResources("input_datasets.txt").stream()
            .flatMap(str -> Arrays.stream(str.split("[\\W\\d]")))
            .filter(str -> !str.isEmpty() && !skipWords.contains(str.toLowerCase()))
            .collect(Collectors.toList());

        // Single processing
        dataset.forEach(singleCMK::setString);
        System.out.println("Single: " + singleCMK.getKTop());

        // Parallel processing
        CountMinSketch parallelCMK = new CountMinSketch(200, 8, 8);
        for(List<String>batch: splitOnBatches(dataset, 200)) {
            CountMinSketch cmk = new CountMinSketch(200, 8, 8);
            batch.forEach(cmk::setString);
            parallelCMK.merge(cmk);
        }
        System.out.println("Parallel: " + parallelCMK.getKTop());

    }

    private static List<String> readStringsFromResources(String filename) throws IOException {
        ClassLoader classLoader = Main.class.getClassLoader();
        String file = classLoader.getResource(filename).getFile();
        return Files.readAllLines(Paths.get(file));
    }

    private static List<List<String>> splitOnBatches(List<String> dataset, int batchSize) {
        List<List<String>> batches = new ArrayList<>();
        List<String> batch = new ArrayList<>();
        for (String data: dataset) {
            if (batch.size() == batchSize) {
                batches.add(batch);
                batch = new ArrayList<>();
            }else if (batch.size() < batchSize) {
                batch.add(data);
            }
        }
        return batches;
    }
}
