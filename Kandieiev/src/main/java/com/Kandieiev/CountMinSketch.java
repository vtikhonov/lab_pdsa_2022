package main.java.com.Kandieiev;


import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Random;

import static jdk.nashorn.internal.objects.NativeMath.abs;
import static jdk.nashorn.internal.objects.NativeMath.min;
import static jdk.nashorn.internal.runtime.ScriptObject.setGlobalObjectProto;

public class CountMinSketch {

    private byte [][] byteTables = null;
    private short [][] shortTables= null;
    private int [][] intTables = null;
    private int size;
    private int func;
    private int[] a ;
    private int[] b ;
    private int[] mersene = {127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535, 131071};
    Random random = new Random();
    int p;

    public CountMinSketch(byte[][] byteTables, int size, int func) {
        this.byteTables = new byte[func][size];
        this.size = size;
        this.func = func;
        a = new int[func];
        b = new int[func];
        p = Arrays.stream(mersene).filter(el -> el > size).findAny().getAsInt();
        for (int i = 0; i < func; i++) {
            a[i] = random.nextInt(p-2)+1;
            b[i] = random.nextInt(p-1);
        }
    }
    public CountMinSketch(short[][] shortTables, int size, int func) {
        this.shortTables = new short[func][size];
        this.size = size;
        this.func = func;
        a = new int[func];
        b = new int[func];
        p = Arrays.stream(mersene).filter(el -> el > size).findAny().getAsInt();
        for (int i = 0; i < func; i++) {
            a[i] = random.nextInt(p-2)+1;
            b[i] = random.nextInt(p-1);
        }
    }
    public CountMinSketch(int[][] intTables, int size, int func) {
        this.intTables = new int[func][size];
        this.size = size;
        this.func = func;
        a = new int[func];
        b = new int[func];
        p = Arrays.stream(mersene).filter(el -> el > size).findAny().getAsInt();
        for (int i = 0; i < func; i++) {
            a[i] = random.nextInt(p-2)+1;
            b[i] = random.nextInt(p-1);
        }
    }

    public void intInsert(int val)
    {
        for (int i = 0; i < func; i++) {
            int hash = hashFunction(val, i);
            if (intTables.length>0)
                intTables[i][hash]++;
        }
    }
    public void shortInsert(int val)
    {
        for (int i = 0; i < func; i++) {
            int hash = hashFunction(val, i);
            shortTables[i][hash]++;
        }
    }
    public void byteInsert(int val)
    {
        for (int i = 0; i < func; i++) {
            int hash = hashFunction(val, i);
            byteTables[i][hash]++;
        }
    }

    private int hashFunction(int val, int number){
        return (int)(((a[number] * (long)val + b[number])% p) % (size));
    }


    public int intSketchCount(int val)
    {
        int [] hashes = new int [func];
        for (int i = 0; i < func; i++) {
            int hash = hashFunction(val, i);
            hashes[i] = intTables[i][hash];
        }
        int min = Arrays.stream(hashes).min().getAsInt();
        return min;
    }

    public int shortSketchCount(int val)
    {
        int [] hashes = new int [func];
        for (int i = 0; i < func; i++) {
            int hash = hashFunction(val, i);
            hashes[i] = shortTables[i][hash];
        }
        int min = Arrays.stream(hashes).min().getAsInt();
        return min;
    }

    public int byteSketchCount(int val)
    {
        int [] hashes = new int [func];
        for (int i = 0; i < func; i++) {
            int hash = hashFunction(val, i);
            hashes[i] = byteTables[i][hash];
        }
        int min = Arrays.stream(hashes).min().getAsInt();
        return min;
    }

    public void intTable(){
        for (int i = 0; i < func; i++) {
            System.out.print("h" + i + ":  ");
            for (int j = 0; j < size; j++) {
                System.out.print(intTables[i][j] + "  ");
            }
            System.out.println("");
        }
    }

    public void shortTable(){
        for (int i = 0; i < func; i++) {
            System.out.print("h" + i + ":  ");
            for (int j = 0; j < size; j++) {
                System.out.print(shortTables[i][j] + "  ");
            }
            System.out.println("");
        }
    }

    public void byteTable(){
        for (int i = 0; i < func; i++) {
            System.out.print("h" + i + ":  ");
            for (int j = 0; j < size; j++) {
                System.out.print(byteTables[i][j] + "  ");
            }
            System.out.println("");
        }
    }
}

