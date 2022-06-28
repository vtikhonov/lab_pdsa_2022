package main.java.com.Kandieiev;

public class Fabric {
    private static byte [][] byteTables;
    private static short [][] shortTables;
    private static int [][] intTables;
    public static CountMinSketch createCMS (int size, int function, String type){
        if(type.equals("byte")) {
            return new CountMinSketch(byteTables, size, function);
        }
        else if (type.equals("short")){
            return new CountMinSketch(shortTables, size, function);
        }
        else if(type.equals("int")){
            return new CountMinSketch(intTables, size, function);
        }
        return null;
    }
}
