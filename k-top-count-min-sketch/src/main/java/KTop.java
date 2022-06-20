import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

class KTop {

    private final Map<String, Integer> maxHeap = new HashMap<>();
    private final int k;

    KTop(int k) {
        this.k = k;
    }

    void add(String key, int frequency) {
        if (maxHeap.get(key) != null) {
            maxHeap.replace(key, frequency);
        } else {
            if (maxHeap.size() < k) {
                maxHeap.put(key, frequency);
            } else {
                String keyForLowestFrequency = Collections.min(maxHeap.entrySet(), Map.Entry.comparingByValue()).getKey();
                if (frequency > maxHeap.get(keyForLowestFrequency)) {
                    maxHeap.remove(keyForLowestFrequency);
                    maxHeap.put(key, frequency);
                }
            }
        }
    }

    void merge(KTop kTop) {
        for (Map.Entry<String, Integer> thatMaxHeapkTop: kTop.maxHeap.entrySet()) {
            if (maxHeap.get(thatMaxHeapkTop.getKey()) != null) {
                int mergedFrequency = thatMaxHeapkTop.getValue() + maxHeap.get(thatMaxHeapkTop.getKey());
                add(thatMaxHeapkTop.getKey(), mergedFrequency);
            } else {
                add(thatMaxHeapkTop.getKey(), thatMaxHeapkTop.getValue());
            }
        }
    }

    int getFrequency(String key) {
        return maxHeap.entrySet().stream()
            .filter(kTopElems -> kTopElems.getKey().equals(key))
            .map(Map.Entry::getValue)
            .findFirst()
            .orElse(0);
    }

    Map<String, Integer> getKTop() {
        return maxHeap;
    }
}
