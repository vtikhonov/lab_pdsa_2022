import jdk.dynalink.linker.LinkerServices;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) throws IOException {
        CountMinSketch countMinSketch = new CountMinSketch(200, 8, 8);

        List<String> skipWords = readStringsFromResources("skip_words.txt").stream()
            .map(String::toLowerCase)
            .collect(Collectors.toList());

        readStringsFromResources("input_datasets.txt").stream()
            .flatMap(str -> Arrays.stream(str.split("[\\W\\d]")))
            .filter(str -> !str.isEmpty() && !skipWords.contains(str.toLowerCase()))
            .forEach(countMinSketch::setString);

        System.out.println(countMinSketch.getKTop());
    }

    private static List<String> readStringsFromResources(String filename) throws IOException {
        ClassLoader classLoader = Main.class.getClassLoader();
        String file = classLoader.getResource(filename).getFile();
        return Files.readAllLines(Paths.get(file));
    }
}
