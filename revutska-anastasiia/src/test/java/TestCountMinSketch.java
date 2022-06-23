import com.revutska.CountMinSketch;
import org.junit.jupiter.api.Test;

import java.util.Random;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class TestCountMinSketch {

    @Test
    public void testWidth() {
        CountMinSketch cms = new CountMinSketch();
        assertEquals(272, cms.getWidth());
    }

    @Test
    public void testDepth() {
        CountMinSketch cms = new CountMinSketch();
        assertEquals(5, cms.getDepth());
    }

    @Test
    public void testSizeInBytes() {
        CountMinSketch cms = new CountMinSketch();
        assertEquals(5448, cms.getSizeInBytes());
        cms = new CountMinSketch(1024, 10, 1, 12);
        assertEquals(40968, cms.getSizeInBytes());
    }

    @Test
    public void testCMSketch() {
        CountMinSketch cms = new CountMinSketch(1024, 10, 2, 12);
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        cms.set("HelloWorld".getBytes());
        System.out.println(cms.getKTop());
        assertEquals(4, cms.getEstimatedCount("Hello".getBytes()));
        assertEquals(1, cms.getEstimatedCount("HelloWorld".getBytes()));

        int[] actualFreq = new int[100];
        Random rand = new Random(123);
        CountMinSketch cms3 = new CountMinSketch();
        for (int i = 0; i < 10000; i++) {
            int idx = rand.nextInt(actualFreq.length);
            cms3.setInt(idx);
            actualFreq[idx] += 1;
        }

        assertEquals(actualFreq[10], cms3.getEstimatedCountInt(10), 0.01);
        assertEquals(actualFreq[20], cms3.getEstimatedCountInt(20), 0.01);
        assertEquals(actualFreq[30], cms3.getEstimatedCountInt(30), 0.01);
        assertEquals(actualFreq[40], cms3.getEstimatedCountInt(40), 0.01);
        assertEquals(actualFreq[50], cms3.getEstimatedCountInt(50), 0.01);
        assertEquals(actualFreq[60], cms3.getEstimatedCountInt(60), 0.01);
    }

    @Test
    public void testMerge() {
        CountMinSketch cms = new CountMinSketch(1024, 10, 4, 12);
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        CountMinSketch cms2 = new CountMinSketch(1024, 10, 4, 12);
        cms2.setString("Hello");
        cms2.setString("Hello");
        cms2.setString("Hello");
        cms2.setString("Hello");
        cms.merge(cms2);
        assertEquals(8, cms.getEstimatedCountString("Hello"));

        int[] actualFreq = new int[100];
        Random rand = new Random(123);
        CountMinSketch cms3 = new CountMinSketch();
        for (int i = 0; i < 10000; i++) {
            int idx = rand.nextInt(actualFreq.length);
            cms3.setInt(idx);
            actualFreq[idx] += 1;
        }

        assertEquals(actualFreq[10], cms3.getEstimatedCountInt(10), 0.01);
        assertEquals(actualFreq[20], cms3.getEstimatedCountInt(20), 0.01);
        assertEquals(actualFreq[30], cms3.getEstimatedCountInt(30), 0.01);
        assertEquals(actualFreq[40], cms3.getEstimatedCountInt(40), 0.01);
        assertEquals(actualFreq[50], cms3.getEstimatedCountInt(50), 0.01);
        assertEquals(actualFreq[60], cms3.getEstimatedCountInt(60), 0.01);

        int[] actualFreq2 = new int[100];
        rand = new Random(321);
        CountMinSketch cms4 = new CountMinSketch();
        for (int i = 0; i < 10000; i++) {
            int idx = rand.nextInt(actualFreq2.length);
            cms4.setInt(idx);
            actualFreq2[idx] += 1;
        }
        cms3.merge(cms4);

        assertEquals(actualFreq[10] + actualFreq2[10], cms3.getEstimatedCountInt(10), 0.01);
        assertEquals(actualFreq[20] + actualFreq2[20], cms3.getEstimatedCountInt(20), 0.01);
        assertEquals(actualFreq[30] + actualFreq2[30], cms3.getEstimatedCountInt(30), 0.01);
        assertEquals(actualFreq[40] + actualFreq2[40], cms3.getEstimatedCountInt(40), 0.01);
        assertEquals(actualFreq[50] + actualFreq2[50], cms3.getEstimatedCountInt(50), 0.01);
        assertEquals(actualFreq[60] + actualFreq2[60], cms3.getEstimatedCountInt(60), 0.01);
    }

    public void testIncompatibleMerge() {
        CountMinSketch cms = new CountMinSketch(1024, 10, 4, 12);
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        cms.set("Hello".getBytes());
        CountMinSketch cms2 = new CountMinSketch(1024, 11, 4, 12);
        cms2.setString("Hello");
        cms2.setString("Hello");
        cms2.setString("Hello");
        cms2.setString("Hello");

        // should throw exception
        assertThrows(RuntimeException.class, () -> cms.merge(cms2));
    }
}