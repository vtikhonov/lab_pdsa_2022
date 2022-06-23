package com.revutska;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static java.nio.charset.StandardCharsets.UTF_8;

/**
 * Count Min sketch is a probabilistic data structure for finding the frequency of events in a
 * stream of data. The data structure accepts two parameters epsilon and delta, epsilon specifies
 * the error in estimation and delta specifies the probability that the estimation is wrong (or the
 * confidence interval). The default values are 1% estimation error (epsilon) and 99% confidence
 * (1 - delta). Tuning these parameters results in increase or decrease in the size of the count
 * min sketch. The constructor also accepts width and depth parameters. The relationship between
 * width and epsilon (error) is width = Math.ceil(Math.exp(1.0)/epsilon). In simpler terms, the
 * lesser the error is, the greater is the width and hence the size of count min sketch.
 * The relationship between delta and depth is depth = Math.ceil(Math.log(1.0/delta)). In simpler
 * terms, the more the depth of the greater is the confidence.
 * The way it works is, if we need to estimate the number of times a certain key is inserted (or appeared in
 * the stream), count min sketch uses pairwise independent hash functions to map the key to
 * different locations in count min sketch and increment the counter.
 * <p/>
 * For example, if width = 10 and depth = 4, lets assume the hashcodes
 * for key "HELLO" using pairwise independent hash functions are 9812121, 6565512, 21312312, 8787008
 * respectively. Then the counter in hashcode % width locations are incremented.
 * <p/>
 * 0   1   2   3   4   5   6   7   8   9
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * <p/>
 * Now for a different key "WORLD", let the hashcodes be 23123123, 45354352, 8567453, 12312312.
 * As we can see below there is a collision for 2nd hashcode
 * <p/>
 * 0   1   2   3   4   5   6   7   8   9
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * --- --- --- --- --- --- --- --- --- ---
 * | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
 * --- --- --- --- --- --- --- --- --- ---
 * <p/>
 * Now, to get the estimated count for key "HELLO", same process is repeated again to find the
 * values in each position and the estimated count will be the minimum of all values (to account for
 * hash collisions).
 * <p/>
 * estimatedCount("HELLO") = min(1, 2, 1, 1)
 * <p/>
 * so even if there are multiple hash collisions, the returned value will be the best estimate
 * (upper bound) for the given key. The actual count can never be greater than this value.
 */
public class CountMinSketch {
    // 1% estimation error with 1% probability (99% confidence) that the estimation breaks this limit
    private static final float DEFAULT_DELTA = 0.01f;
    private static final float DEFAULT_EPSILON = 0.01f;
    private static final int DEFAULT_K = 10000;
    private final int w;
    private final int d;
    private final int[][] multiset;
    private final KTop kTop;
    private final int numberOfBitsPerCounter;

    public CountMinSketch() {
        this(DEFAULT_DELTA, DEFAULT_EPSILON, DEFAULT_K);
    }

    public CountMinSketch(float delta, float epsilon, int k) {
        this.w = (int) Math.ceil(Math.exp(1.0) / epsilon);
        this.d = (int) Math.ceil(Math.log(1.0 / delta));
        this.multiset = new int[d][w];
        this.kTop = new KTop(k);
        this.numberOfBitsPerCounter = 32;
    }

    public CountMinSketch(int width, int depth, int k, int numberOfBitsPerCounter) {
        this.w = width;
        this.d = depth;
        this.multiset = new int[d][w];
        this.kTop = new KTop(k);
        this.numberOfBitsPerCounter = numberOfBitsPerCounter;
    }

    public int getWidth() {
        return w;
    }

    public int getDepth() {
        return d;
    }

    public List<Map.Entry<String, Integer>> getKTop() {
        return kTop.getKTop().entrySet().stream().sorted(Map.Entry.comparingByValue(Comparator.reverseOrder())).collect(Collectors.toList());
    }

    /**
     * Returns the size in bytes after serialization.
     *
     * @return serialized size in bytes
     */
    public long getSizeInBytes() {
        return ((w * d) + 2) * (Integer.SIZE / 8);
    }

    public void set(byte[] key) {
        for (int i = 1; i <= d; i++) {
            int pos = getColumnNum(key, i);
            multiset[i - 1][pos] += 1;
        }
        saveFrequencyInKTop(key);
    }

    private void saveFrequencyInKTop(byte[] key) {
        int min = Integer.MAX_VALUE;
        for (int i = 1; i <= d; i++) {
            int pos = getColumnNum(key, i);
            min = Math.min(min, multiset[i - 1][pos]);
        }
        kTop.add(new String(key, UTF_8), min);
    }

    private int getColumnNum(byte[] key, int i) {
        // Lets split up 64-bit hashcode into two 32-bit hashcodes and employ the technique mentioned
        // in the above paper

        long hash64 = Murmur3.hash64(key);

        int hash1 = (int) hash64;
        int hash2 = (int) (hash64 >>> numberOfBitsPerCounter);

        int combinedHash = hash1 + (i * hash2);
        // hashcode should be positive, flip all the bits if it's negative
        if (combinedHash < 0) {
            combinedHash = ~combinedHash;
        }
        return combinedHash % w;
    }

    public void setString(String val) {
        set(val.getBytes());
    }

    public void setByte(byte val) {
        set(new byte[]{val});
    }

    public void setInt(int val) {
        // puts int in little endian order
        set(intToByteArrayLE(val));
    }


    public void setLong(long val) {
        // puts long in little endian order
        set(longToByteArrayLE(val));
    }

    public void setFloat(float val) {
        setInt(Float.floatToIntBits(val));
    }

    public void setDouble(double val) {
        setLong(Double.doubleToLongBits(val));
    }

    private static byte[] intToByteArrayLE(int val) {
        return new byte[]{(byte) (val >> 0),
            (byte) (val >> 8),
            (byte) (val >> 16),
            (byte) (val >> 24)};
    }

    private static byte[] longToByteArrayLE(long val) {
        return new byte[]{(byte) (val >> 0),
            (byte) (val >> 8),
            (byte) (val >> 16),
            (byte) (val >> 24),
            (byte) (val >> 32),
            (byte) (val >> 40),
            (byte) (val >> 48),
            (byte) (val >> 56),};
    }

    public int getEstimatedCount(byte[] key) {
        return kTop.getFrequency(new String(key, UTF_8));
    }

    public int getEstimatedCountString(String val) {
        return getEstimatedCount(val.getBytes());
    }

    public int getEstimatedCountByte(byte val) {
        return getEstimatedCount(new byte[]{val});
    }

    public int getEstimatedCountInt(int val) {
        return getEstimatedCount(intToByteArrayLE(val));
    }

    public int getEstimatedCountLong(long val) {
        return getEstimatedCount(longToByteArrayLE(val));
    }

    public int getEstimatedCountFloat(float val) {
        return getEstimatedCountInt(Float.floatToIntBits(val));
    }

    public int getEstimatedCountDouble(double val) {
        return getEstimatedCountLong(Double.doubleToLongBits(val));
    }

    /**
     * Merge the give count min sketch with current one. Merge will throw RuntimeException if the
     * provided com.revutska.CountMinSketch is not compatible with current one.
     *
     * @param that - the one to be merged
     */
    public void merge(CountMinSketch that) {
        if (that == null) {
            return;
        }

        if (this.w != that.w) {
            throw new RuntimeException("Merge failed! Width of count min sketch do not match!" +
                "this.width: " + this.getWidth() + " that.width: " + that.getWidth());
        }

        if (this.d != that.d) {
            throw new RuntimeException("Merge failed! Depth of count min sketch do not match!" +
                "this.depth: " + this.getDepth() + " that.depth: " + that.getDepth());
        }

        kTop.merge(that.kTop);
    }
}