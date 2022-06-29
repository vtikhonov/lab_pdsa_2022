package main.java.com.Kandieiev;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.text.DecimalFormat;
import java.util.*;
import java.util.stream.Collectors;

public class Main {
    static CountMinSketch cms;

    public static void main(String[] args) throws IOException {

        String file = args[0]; // input file
        String c = args[1]; // byte, short, int
        int k = Integer.valueOf(args[2]); // number of top frequent
        int p = Integer.valueOf(args[3]); // amount hash function
        int m = Integer.valueOf(args[4]); //buffer size
        cms = Fabric.createCMS(m, p, c);

        String text = readFile(file);
        text = text.toLowerCase(Locale.ROOT);
        text = text.replaceAll("[^A-Za-z ]", "");
        text = deleteWords("skip_words.txt", text);

        Arrays.stream(text.split(" ")).forEach(e -> cms.insert(Math.abs(e.hashCode())));

        Map<String, Integer> sorted =  sortMap(getMap(text.split(" ")), k+2);
        buildTable(sorted, c);
    }

    public static String readFile(String path) throws IOException {
        return new String(Files.readAllBytes(Paths.get(path)));
    }

    public static String deleteWords(String path, String text) throws IOException{
        String words = readFile(path);
        String [] banWord = words.split("\n");
        for (int i = 0; i < banWord.length; i++) {
            banWord[i] = banWord[i].replaceAll("[^A-Za-z ]", "");  // not know why, but without it, filter not working. (try make this in stream, but take much longer time)
        }
        String result = Arrays.stream(text.split(" "))
                .filter(el -> Arrays.stream(banWord).noneMatch(el::equals))
                .collect(Collectors.joining(" "));
        return result;
    }

    public static Map<String, Integer> getMap (String [] words){
        HashMap<String,Integer> map = new HashMap<String,Integer>();
        for (String word: words) {
            if(map.containsKey(word)){
                map.put(word, map.get(word)+1);
            }
            else {
                map.put(word, 1);
            }
        }
        return map;
    }
    public static Map <String, Integer> sortMap(Map<String , Integer> map, int limit){
        Map<String,Integer> sorted =
                map.entrySet().stream()
                        .sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
                        .limit(limit)
                        .collect(Collectors.toMap(
                                Map.Entry::getKey, Map.Entry::getValue, (e1, e2) -> e1, LinkedHashMap::new));
        return sorted;
    }

    public static void buildTable(Map <String, Integer> sorted, String type){
        int freq_approx;
        String s = sorted.toString().replaceAll("\\{\\}", "");
        System.out.println("++++++++++++++++++++++++++++++++++++++++++++++");
        System.out.println("+      word       +   ref  + approx + error  +");
        System.out.println("++++++++++++++++++++++++++++++++++++++++++++++");
        for (int i = 1; i < s.split(",").length-1; i++) {
            String word = s.split(",")[i].split("=")[0].replaceAll(" ", "");
            int freq_ref = Integer.valueOf(s.split(",")[i].split("=")[1]);
            freq_approx = cms.sketchCount(Math.abs(word.hashCode()));
            if (freq_approx < 0){
                freq_approx = cms.getMaximum_cell_value() + freq_approx;
            }
            System.out.format("+ %15s + %6s + %6s + %6s +%n", new String[]{word, Integer.toString(freq_ref), Integer.toString(freq_approx), new DecimalFormat("#0.00").format(Math.abs((double)(freq_approx - freq_ref)/freq_ref) * 100)});
        }

    }
}
