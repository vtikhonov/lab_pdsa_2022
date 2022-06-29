import numpy as np
import codecs
import pandas as pd
import argparse

ROOT: str = "MartyniukAndrii/"

DELTA: float = 0.02
EPSILON: float = 0.005
DELTA_EPSILON: float = 2.7182

K: int = 10
M: int = int(DELTA_EPSILON / EPSILON)
P: int = int(np.log(1 / DELTA))


def out_put_arguments():
    configuration = argparse.ArgumentParser()
    configuration.add_argument('--file_path', type=str, required=False, default=ROOT + 'text.txt')
    configuration.add_argument('-k', type=int, required=False, default=K)
    configuration.add_argument('-m', type=int, required=False, default=M)
    configuration.add_argument('-p', type=int, required=False, default=P)
    configuration.add_argument('-c', type=int, required=False, default=32, choices=[8, 16, 32])
    return configuration


def split(txt, seps):
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]


def create_cm_sketch(data):
    count_min_sketch = None
    if C == 8:
        count_min_sketch = np.zeros((P, M), dtype='uint8')
    elif C == 16:
        count_min_sketch = np.zeros((P, M), dtype='uint16')
    elif C == 32:
        count_min_sketch = np.zeros((P, M), dtype='uint32')
    for w in data:
        for j in range(P):
            i = hash(w + str(j)) % M
            count_min_sketch[j, i] += 1
    return count_min_sketch


def count_min_frequency_estimation(word, count_min_sketch):
    frequency = []
    for i in range(P):
        word_hash = hash(word + str(i)) % M
        frequency.append(count_min_sketch[i, word_hash])
    return min(frequency)


def count_exact_word_frequency(data):
    frequency = {}
    for word in data:
        if word not in frequency.keys():
            frequency[word] = 1
        else:
            frequency[word] += 1
    sorted_frequency = sorted(frequency.items(), key=lambda item: int(item[1]), reverse=True)
    return sorted_frequency


def get_top_frequency_elements(data, count_min_sketch):
    top_frequency_elements = []
    for word in data:
        if word in top_frequency_elements:
            pass
        elif len(top_frequency_elements) < K:
            top_frequency_elements.append(word)
        else:
            frequency_word = count_min_frequency_estimation(word, count_min_sketch)
            new_top_frequency_elements = {word: count_min_frequency_estimation(word, count_min_sketch) for word in
                                          top_frequency_elements}
            sorted_new_top_frequency_elements = sorted(new_top_frequency_elements.items(),
                                                       key=lambda item: int(item[1]))
            min_word = min(new_top_frequency_elements, key=new_top_frequency_elements.get)
            min_frequency = new_top_frequency_elements.get(min_word)
            if frequency_word > min_frequency:
                top_frequency_elements.append(word)
                top_frequency_elements.remove(min_word)
    return top_frequency_elements


def save_result(count_min_sketch_frequency, exact_frequency):
    count_min_sketch_frequency = dict(
        sorted(count_min_sketch_frequency.items(), key=lambda item: int(item[1]), reverse=True))
    dataframe = pd.DataFrame({'word': list(count_min_sketch_frequency.keys()),
                              'frequency_approx': list(count_min_sketch_frequency.values())})
    exact_frequency = dict(exact_frequency)
    frequency_reference = []
    for w in count_min_sketch_frequency.keys():
        frequency_reference.append(int(exact_frequency[w]))
    dataframe.insert(1, 'frequency_ref', np.array(frequency_reference), True)
    error = []
    for ref, approx in zip(frequency_reference, count_min_sketch_frequency.values()):
        error.append(100 * abs(approx - ref) / ref)
    dataframe.insert(3, 'error', np.array(error), True)
    dataframe.to_csv(ROOT + 'result.csv', index=False)
    return dataframe


if __name__ == "__main__":
    config = out_put_arguments().parse_args()
    file_path = config.file_path
    K = config.k
    M = config.m
    P = config.p
    C = config.c
    print('file_path: ', file_path)
    print('k: ', K)
    print('m: ', M)
    print('p: ', P)
    print('c: ', C)

    # separators list
    separators = [' ', ',', '.', ':', ';', '!', '?', '—', '(', ')', '[', ']', '{', '}', '”', '“', '/', '\n']

    # list of words to skip
    words_skip_file = open(ROOT + 'skip_words.txt', 'r')
    skipped_words = words_skip_file.read()
    skipped_words = skipped_words.split('\n')
    words_skip_file.close()

    # list of all words in text
    reading_file = codecs.open(file_path, "r", "utf_8_sig")
    text = reading_file.read()
    words = split(text, separators)
    words = [word.lower() for word in words if word.lower() not in skipped_words]
    reading_file.close()

    # frequency by count min sketch
    sketch = create_cm_sketch(words)
    extra_words_list = get_top_frequency_elements(words, sketch)
    frequency_cm_sketch = {word: count_min_frequency_estimation(word, sketch) for word in extra_words_list}

    # exact frequency
    frequency_exact = count_exact_word_frequency(words)

    # save and print result
    result = save_result(frequency_cm_sketch, frequency_exact)
    print(result)
