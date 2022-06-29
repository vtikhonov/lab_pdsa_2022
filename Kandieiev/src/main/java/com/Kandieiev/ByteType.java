package main.java.com.Kandieiev;

import java.util.Arrays;

public class ByteType extends CountMinSketch{
    private byte [][] byteTables;
    public ByteType(int size, int func) {
        super(size, func);
        this.byteTables = new byte[func][size];
        this.maximum_cell_value = (int) (Math.pow(2, 8));
    }

    @Override
    public void insert(int val) {
        for (int i = 0; i < getFunc(); i++) {
            int hash = hashFunction(val, i);
            if (byteTables[i][hash] != -1) {
                byteTables[i][hash]++;
            }
        }
    }

    @Override
    public int sketchCount(int val) {
        int [] hashes = new int [getFunc()];
        for (int i = 0; i < getFunc(); i++) {
            int hash = hashFunction(val, i);
            hashes[i] = byteTables[i][hash];
        }
        int min = Arrays.stream(hashes).min().getAsInt();
        return min;
    }

    @Override
    public void table() {
        for (int i = 0; i < getFunc(); i++) {
            System.out.print("h" + i + ":  ");
            for (int j = 0; j < getSize(); j++) {
                System.out.print(byteTables[i][j] + "  ");
            }
            System.out.println("");
        }
    }

}
