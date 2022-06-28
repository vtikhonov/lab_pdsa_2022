package main.java.com.Kandieiev;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
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

        if (c.equals("int")) {
            Arrays.stream(text.split(" ")).forEach(e -> cms.intInsert(Math.abs(e.hashCode())));
            cms.intTable();
        }
        if (c.equals("short")) {
            Arrays.stream(text.split(" ")).forEach(e -> cms.shortInsert(Math.abs(e.hashCode())));
            cms.shortTable();
        }
        if (c.equals("byte")) {
            Arrays.stream(text.split(" ")).forEach(e -> cms.byteInsert(Math.abs(e.hashCode())));
            cms.byteTable();
        }


        Map<String, Integer> sorted =  sortMap(getMap(text.split(" ")), k+2);
        buildTable(sorted, c);
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
            if(type.equals("int")) {
                freq_approx = cms.intSketchCount(Math.abs(word.hashCode()));
            }
            else if(type.equals("short")) {
                freq_approx = cms.shortSketchCount(Math.abs(word.hashCode()));
            }
            else{
                freq_approx = cms.byteSketchCount(Math.abs(word.hashCode()));
            }
            System.out.format("+ %15s + %6s + %6s + %6s +%n", new String[]{word, Integer.toString(freq_ref), Integer.toString(freq_approx), Integer.toString(100*freq_ref/freq_approx)});
        }

    }
}
