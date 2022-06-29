import numpy as np
import string
import argparse
import random
from operator import itemgetter
import array

prime_numbers = [127, 521, 607, 1279, 2203, 2281, 3217, 4253, 4423, 9689,
                 9941, 11213, 19937, 21701, 23209, 44497, 86243, 110503, 132049, 216091]


class HashFunction:
    def __init__(self, x, y, prime, buffer):
        self.x = x
        self.y = y
        self.prime = prime
        self.buffer = buffer

    def getHashValue(self, character):
        hash_val = hash(character)
        if (hash_val < 0):
            hash_val = abs(hash_val)
        return self.calculateHash(hash_val, self.x, self.y, self.prime)

    def calculateHash(self, hash, x, y, prime):
        return ((self.x * hash + self.y) % self.prime) % self.buffer


def get_words_list(path_to_file):
    to_skip = []
    with open("skip_words.txt", "r") as skip:
        for line in skip:
            for word in line.split():
                to_skip.append(word)

    arr = []

    with open(path_to_file, "r") as oz:
        for line in oz:
            for word in line.split():
                word = word.translate(str.maketrans('', '', string.punctuation))
                word = word.lower()
                word = word.replace('“', '')
                word = word.replace('”', '')
                if word not in to_skip and word != "":
                    arr.append(word)

    return arr


def count_min_scetch(input_path, k, m, p, c):

    hash_functions = []
    for i in range(p):
        prime_num = m - 1
        while prime_num < m:
            prime_num = random.choice(prime_numbers)
        h = HashFunction(2*random.randint(1, 5000)+1, 2*random.randint(1, 5000)+1, prime_num, m)

        hash_functions.append(h)

    if c <= 8:
        size = "B"
    elif c <= 16:
        size = "I"
    else:
        size = "L"

    sketch = [array.array(size, (0 for _ in range(m))) for _ in range(p)]
    arr = get_words_list(input_path)
    for word in arr:
        hashes = [i.getHashValue(word) for i in hash_functions]
        for i in range(p):
            try:
                sketch[i][hashes[i]] += 1
            except:
                sketch[i] = array.array("I", sketch[i])
                sketch[i][hashes[i]] += 1

    freq_dict = {}
    for i in list(set(arr)):
        hashes = [k.getHashValue(i) for k in hash_functions]
        result = []
        for j in range(p):
            result.append(sketch[j][hashes[j]])

        freq_dict[i] = min(result)
        # print(freq_dict)
        # print(min(freq_dict.values()))
        if len(freq_dict) > k:
            for ke in freq_dict:
                if freq_dict[ke] == min(freq_dict.values()):
                    freq_dict.pop(ke)
                    break
    return freq_dict


def get_real_freq(input_path, words):
    arr = get_words_list(input_path)
    freq_dict = {}
    for i in words:
        freq_dict[i] = arr.count(i)
    return freq_dict


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch')
    parser.add_argument('-input', type=str, help='path to file or folder with a textual file', required=True)
    parser.add_argument('-k', type=int, help='number of top frequent element that we are looking for', required=True)
    parser.add_argument('-m', type=int, help='count-min sketch buffer size', required=True)
    parser.add_argument('-p', type=int, help='number of independent hash functions', required=True)
    parser.add_argument('-c', type=int, default=12, help='number of bits per counter, default is 12', required=True)

    args = parser.parse_args()

    path_to_file = args.input
    k = args.k
    m = args.m
    p = args.p
    c = args.c

    scetch_results = count_min_scetch(path_to_file, k, m, p,c)
    reference_results = get_real_freq(path_to_file, list(scetch_results.keys()))
    final_list = [("word", "freq_ref", "freq_approx", "error")]
    for i in scetch_results:
        err = round(abs(reference_results[i] - scetch_results[i]) / reference_results[i] * 100, 3)
        final_list.append((i, reference_results[i], scetch_results[i], err))
    print(*final_list, sep="\n")

