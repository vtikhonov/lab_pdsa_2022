package main.java.com.Kandieiev;


import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Random;

import static jdk.nashorn.internal.objects.NativeMath.abs;
import static jdk.nashorn.internal.objects.NativeMath.min;
import static jdk.nashorn.internal.runtime.ScriptObject.setGlobalObjectProto;

public abstract class CountMinSketch {
    private int size;
    private int func;
    private int[] a ;
    private int[] b ;
    private int[] mersene = {127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535, 131071};
    Random random = new Random();
    int p;
    int maximum_cell_value;

    public CountMinSketch(int size, int func) {
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

    public void insert(int val)
    {
        //placeholder
    }

    protected int hashFunction(int val, int number){
        return (int)(((a[number] * (long)val + b[number])% p) % (size));
    }


    public int sketchCount(int val)
    {
        return 0;
    }

    public void table(){
        //placeholder
    }

    public int getSize() {
        return size;
    }

    public void setSize(int size) {
        this.size = size;
    }

    public int getFunc() {
        return func;
    }

    public void setFunc(int func) {
        this.func = func;
    }

    public int[] getA() {
        return a;
    }

    public void setA(int[] a) {
        this.a = a;
    }

    public int[] getB() {
        return b;
    }

    public void setB(int[] b) {
        this.b = b;
    }

    public int getP() {
        return p;
    }

    public void setP(int p) {
        this.p = p;
    }

    public int getMaximum_cell_value() {
        return maximum_cell_value;
    }

    public void setMaximum_cell_value(int maximum_cell_value) {
        this.maximum_cell_value = maximum_cell_value;
    }
}

