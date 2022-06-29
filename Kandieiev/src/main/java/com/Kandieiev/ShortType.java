package main.java.com.Kandieiev;

import java.util.Arrays;

public class ShortType extends CountMinSketch{

    private short [][] shortTables;
    public ShortType(int size, int func) {
        super(size, func);
        this.shortTables = new short[func][size];
        this.maximum_cell_value = (int) (Math.pow(2, 16)/2 -1);
    }

    @Override
    public void insert(int val) {
        for (int i = 0; i < getFunc(); i++) {
            int hash = hashFunction(val, i);
            if (shortTables[i][hash] < getMaximum_cell_value())
                shortTables[i][hash]++;
        }
    }

    @Override
    public int sketchCount(int val) {
        int [] hashes = new int [getFunc()];
        for (int i = 0; i < getFunc(); i++) {
            int hash = hashFunction(val, i);
            hashes[i] = shortTables[i][hash];
        }
        int min = Arrays.stream(hashes).min().getAsInt();
        return min;
    }

    @Override
    public void table() {
        for (int i = 0; i < getFunc(); i++) {
            System.out.print("h" + i + ":  ");
            for (int j = 0; j < getSize(); j++) {
                System.out.print(shortTables[i][j] + "  ");
            }
            System.out.println("");
        }
    }
}
