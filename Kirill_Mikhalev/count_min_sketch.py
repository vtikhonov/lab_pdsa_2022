import pprint
from array import array

import numpy as np
import argparse
import random
import re
from operator import itemgetter

numbers = [521, 607, 1609, 1613, 1619, 1693,	1697, 1699,1709,1721,1753,
           1759,1777,1783, 3499, 3511, 3517, 3527,3529,3533,3539, 110503, 132049, 216091]

class MyHash:
    def __init__(self, num1, num2, prime, limit_size):
        self.num1 = num1
        self.num2 = num2
        self.prime = prime
        self.limit_size = limit_size

    def getHash(self, character):
        hash_val = hash(character)
        if (hash_val < 0):
            hash_val = abs(hash_val)
        return self.makeHash(hash_val, self.num1, self.num2, self.prime)

    def makeHash(self, hash, num1, num2, prime):
        return ((self.num1 * hash + self.num2) % self.prime) % self.limit_size


def get_all_words(path_to_file):
    to_skip = []
    with open("Kirill_Mikhalev\skip_word.txt", "r") as words:
        for line in words:
            for word in line.split():
                to_skip.append(word)

    all_words = []

    with open(path_to_file, "r", encoding="UTF-8") as text:
        for line in text:
            for word in line.split():
                word = word.lower()
                pattern = "[':;,.!?“”_]"
                word = re.sub(pattern, "", word)
                if isinstance(word,int):
                    print("**********")
                if word not in to_skip and word != "":
                    all_words.append(word)
    return all_words

def get_real_freq(input_path, words):
    arr = get_all_words(input_path)
    freq_dict = {}
    for i in words:
        freq_dict[i] = arr.count(i)
    return freq_dict


if __name__ == '__main__':
    params = argparse.ArgumentParser()
    params.add_argument('-input', type=str, required=True)
    params.add_argument('-k', type=int, required=True)
    params.add_argument('-m', type=int, required=True)
    params.add_argument('-p', type=int, required=True)
    params.add_argument('-c', type=int,default=12, required=False)
    params = params.parse_args()
    path_to_file = params.input
    k = params.k
    m = params.m
    p = params.p
    c = params.c

    if c > 16:
        len_type = "L"
    elif c >= 8:
        len_type = "I"
    else:
        len_type = "B"

    hashes = []
    for i in range(p):
        h = MyHash(random.randint(10, 2500), random.randint(10, 2500), random.choice(numbers), m)
        hashes.append(h)
    # sketch = np.zeros([p, m])
    all_words = get_all_words(path_to_file)
    sketch = [array(len_type, (0 for i in range(m))) for j in range(p)]

    for word in all_words:
        my_hashes = [i.getHash(word) for i in hashes]
        for i in range(p):
            sketch[i][my_hashes[i]] += 1

    freq_dict = {}
    for i in list(set(all_words)):
        my_hashes = [k.getHash(i) for k in hashes]
        result = []
        for j in range(p):
            result.append(sketch[j] [my_hashes[j]])
        freq_dict[i] = min(result)
        if len(freq_dict) > k:
            min_element= min(freq_dict.values())
            for word in freq_dict:
                if freq_dict[word] == min_element:
                    freq_dict.pop(word)
                    break
    scetch_results = freq_dict
    reference_results = get_real_freq(path_to_file, list(scetch_results.keys()))
    final_list = [("word", "freq_real", "freq_count_min", "errors")]
    for i in scetch_results:
        err = round(abs(reference_results[i] - scetch_results[i]) / reference_results[i] * 100, 2)
        final_list.append((i, reference_results[i], scetch_results[i], err))
    pprint.pprint(final_list, indent=2, width=80)

