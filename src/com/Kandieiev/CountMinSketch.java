package com.Kandieiev;

import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Random;

import static jdk.nashorn.internal.objects.NativeMath.abs;
import static jdk.nashorn.internal.objects.NativeMath.min;
import static jdk.nashorn.internal.runtime.ScriptObject.setGlobalObjectProto;

public class CountMinSketch {

    String text;
    private int[] h1;
    private int[] h2;
    private int[] h3;
    private int[] h4;
    private int[] h5;
    private int[] h6;
    private static int size;
    private int[] a = new int[6];
    private int[] b = new int[6];
    private int[] mersene = {31, 127, 8191};
    Random random = new Random();
    int p = 127;

    public CountMinSketch(int size) {
        this.size = size;
        h1 = new int[size];
        h2 = new int[size];
        h3 = new int[size];
        h4 = new int[size];
        h5 = new int[size];
        h6 = new int[size];
        for (int i = 0; i < 6; i++) {
            a[i] = random.nextInt(p-2)+1;
            b[i] = random.nextInt(p-1);
        }
    }

    public void insert(int val)
    {
        int hash1 = hashFunction(val, 0);
        int hash2 = hashFunction(val, 1);
        int hash3 = hashFunction(val, 2);
        int hash4 = hashFunction(val, 3);
        int hash5 = hashFunction(val, 4);
        int hash6 = hashFunction(val, 5);

        h1[ hash1 ]++;
        h2[ hash2 ]++;
        h3[ hash3 ]++;
        h4[ hash4 ]++;
        h5[ hash5 ]++;
        h6[ hash6 ]++;
    }

    public int hashFunction(int val, int number){
        return (int)(((a[number] * (long)val + b[number])% p) % (size));
    }

    public int sketchCount(int val)
    {
        int hash1 = hashFunction(val, 0);
        int hash2 = hashFunction(val, 1);
        int hash3 = hashFunction(val, 2);
        int hash4 = hashFunction(val, 3);
        int hash5 = hashFunction(val, 4);
        int hash6 = hashFunction(val, 5);
        int [] hashes= {h1[hash1], h2[hash2], h3[hash3], h4[hash4], h5[hash5], h6[hash6]};

        int min = Arrays.stream(hashes).min().getAsInt();
        return min;
    }

    public void table(){
        System.out.print("h1 : ");
        for (int i = 0; i < size; i++)
            System.out.print(h1[i] +" ");
        System.out.print("\nh2 : ");
        for (int i = 0; i < size; i++)
            System.out.print(h2[i] +" ");
        System.out.print("\nh3 : ");
        for (int i = 0; i < size; i++)
            System.out.print(h3[i] +" ");
        System.out.print("\nh4 : ");
        for (int i = 0; i < size; i++)
            System.out.print(h4[i] +" ");
        System.out.print("\nh5 : ");
        for (int i = 0; i < size; i++)
            System.out.print(h5[i] +" ");
        System.out.print("\nh6 : ");
        for (int i = 0; i < size; i++)
            System.out.print(h6[i] +" ");
        System.out.println("");
    }
}
