package main.java.com.Kandieiev;

import java.util.Arrays;

public class IntType extends CountMinSketch{

    private int [][] intTables = null;
    public IntType(int size, int func) {
        super(size, func);
        this.intTables = new int[func][size];
        this.maximum_cell_value = (int) (Math.pow(2, 32)/2 -1);
    }

    @Override
    public void insert(int val) {
        for (int i = 0; i < getFunc(); i++) {
            int hash = hashFunction(val, i);
            if (intTables[i][hash] < getMaximum_cell_value())
                intTables[i][hash]++;
        }
    }

    @Override
    public int sketchCount(int val) {
        int [] hashes = new int [getFunc()];
        for (int i = 0; i < getFunc(); i++) {
            int hash = hashFunction(val, i);
            hashes[i] = intTables[i][hash];
        }
        int min = Arrays.stream(hashes).min().getAsInt();
        return min;
    }

    @Override
    public void table() {
        for (int i = 0; i < getFunc(); i++) {
            System.out.print("h" + i + ":  ");
            for (int j = 0; j < getSize(); j++) {
                System.out.print(intTables[i][j] + "  ");
            }
            System.out.println("");
        }
    }
}
