package main.java.com.Kandieiev;

public class Fabric {

    public static CountMinSketch createCMS (int size, int function, String type){
        if(type.equals("byte")) {
            return new ByteType(size, function);
        }
        else if (type.equals("short")){
            return new ShortType(size, function);
        }
        else if(type.equals("int")){
            return new IntType(size, function);
        }
        return null;
    }
}
