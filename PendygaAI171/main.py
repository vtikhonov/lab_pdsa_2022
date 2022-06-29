import numpy as np
import argparse
import array
import re
import random
from operator import itemgetter
import pandas as pd

primes = (7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281, 3217, 1281, 4423, 9689, 9941, 11213, 19937, 21701)  # Mersenne primes
separators = "[':;,.!?“”_]"
delta = 0.02
epsilon = 0.005

def newParsing():  # creating arguments for command line parsing
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation')
    parser.add_argument('--input',
                        type=str,
                        help='Path to file or folder with a textual file',
                        required=False,
                        default='98-0.txt')
    parser.add_argument('-k',
                        type=int,
                        help='Number of top frequent element that we are looking for.',
                        required=False,
                        default=10)
    parser.add_argument('-m',
                        type=int,
                        help='Count-min sketch buffer size',
                        required=False,
                        default=int(np.e / epsilon))  # w
    parser.add_argument('-p',
                        type=int,
                        help='Number of independent hash functions',
                        required=False,
                        default=int(np.log(1 / delta)))  # d
    parser.add_argument('-c',
                        type=int,
                        default=32,
                        help='number of bits per counter, default is 12',
                        required=False,
                        choices=[8, 16, 32])
    return parser

class HashFunc:
    def __init__(self, a, b, prime, limit_size):
        self.a = a
        self.b = b
        self.prime = prime
        self.limit_size = limit_size

    def get_hash(self, character):
        hash_val = hash(character)
        if (hash_val < 0):
            hash_val = abs(hash_val)
        return self.make_hash(hash_val, self.a, self.b, self.prime)

    def make_hash(self, hash, a, b, prime):
        return ((self.a * hash + self.b) % self.prime) % self.limit_size

def getAllwords(input):
    to_skip = []
    with open("skip_words.txt", "r") as words:
        for line in words:
            for word in line.split():
                to_skip.append(word)

    all_words = []

    with open(input, "r", encoding="UTF-8") as text:
        for line in text:
            for word in line.split():
                word = word.lower()
                word = re.sub(separators, "", word)
                if isinstance(word, int):
                    print("**********")
                if word not in to_skip and word != "":
                    all_words.append(word)
    return all_words

def realFreq(input_path, words):
    arr = getAllwords(input_path)
    freq_dict = {}
    for i in words:
        freq_dict[i] = arr.count(i)
    return freq_dict


parser = newParsing().parse_args()
input = parser.input
k = parser.k
m = parser.m
p = parser.p
c = parser.c
print('input: ', input)
print('k:', k)
print('m: ', m)
print('p: ', p)
print('c: ', c)

len_type = None

if c <= 8:
    len_type ="B"
elif c <= 16:
    len_type = "H"
elif c <= 32:
    len_type = "I"
else:
    len_type = "L"

hashes = []
for i in range(p):
    h = HashFunc(random.randint(10, 2500), random.randint(10, 2500), random.choice(primes), m)
    hashes.append(h)
all_words = getAllwords(input)
sketch = [array.array(len_type, (0 for i in range(m))) for j in range(p)]

for word in all_words:
    myHash = [i.get_hash(word) for i in hashes]
    for i in range(p):
        sketch[i][myHash[i]] += 1

freq_dict = {}
for i in list(set(all_words)):
    myHash = [k.get_hash(i) for k in hashes]
    result = []
    for j in range(p):
        result.append(sketch[j] [myHash[j]])
    freq_dict[i] = min(result)
    freq_dict = dict(sorted(freq_dict.items(), key=itemgetter(1), reverse=True)[:k])

freq_approx = freq_dict
freq_ref = realFreq(input, list(freq_approx.keys()))

def result_view(cm_sketch_freq, exact_freq):
    cm_sketch_freq = dict(sorted(cm_sketch_freq.items(), key=lambda item: int(item[1]), reverse=True))
    df = pd.DataFrame({'word': list(cm_sketch_freq.keys()), 'freq_approx': list(cm_sketch_freq.values())})
    exact_freq = dict(exact_freq)
    freq_ref = []
    for w in cm_sketch_freq.keys():
        freq_ref.append(int(exact_freq[w]))
    df.insert(1, 'freq_ref', freq_ref, True)
    error = []
    for ref, approx in zip(freq_ref, cm_sketch_freq.values()):
        error.append(100 * abs(approx - ref) / ref)
    df.insert(3, 'error', error, True)
    return df

output_res = result_view(freq_approx, freq_ref)
print(result_view(freq_approx, freq_ref))
open('result.txt', 'w').write(output_res.to_string())