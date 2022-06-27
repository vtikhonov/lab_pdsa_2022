"""
Written by Denis Rudnitskiy (@DeNRuDi) 2022
"""
from typing import Dict
import multiprocessing as mp
import argparse
import tabulate
import hashlib
import random
import array
import time
import csv
import io
import os
import re

PRIMES = (7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203,
          2281, 3217, 1281, 4423, 9689, 9941, 11213, 19937, 21701)
PATTERN = re.compile(r'[(),.:;!?\n\t\'\\[\]"]')


def create_parser():
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation')
    parser.add_argument('--input', type=str, help='Path to file or folder with a textual file', required=True)
    parser.add_argument('--skip-file', type=argparse.FileType('r', encoding="UTF-8"), required=False)
    parser.add_argument('--parallel', nargs='?', const=True, required=False)
    parser.add_argument('--hash', type=str, required=False,
                        choices=["sha1", "sha224", "sha256", "sha384", "sha512", "md5"])
    parser.add_argument('-k', type=int, help='Number of top frequent element that we are looking for', required=True)
    parser.add_argument('-m', type=int, help='Count-min sketch buffer size', required=True)
    parser.add_argument('-p', type=int, help='number of independent hash functions', required=True)
    parser.add_argument('-c', type=int, default=12, help='number of bits per counter, default is 12', required=True)
    parser.add_argument('--csv', nargs='?', const=True, help='Create CSV file')
    return parser


def get_skip_words(file: io.FileIO) -> set:
    return {line.strip() for line in file.readlines()}


class CountMinSketch:
    __slots__ = ["frequently", "size", "hash_func", "count", "skip_words", "ccsv", "_filter_words", "backet"]

    def __init__(self, frequently, size, hash_func, count, ccsv=None, skip_words=None):
        self.frequently = frequently  # k
        self.size = size  # m
        self.hash_func = hash_func  # p
        self.count = count  # c
        self.skip_words = skip_words
        self.ccsv = ccsv
        self._filter_words = []
        self.backet = [array.array(self.get_size(), (0 for _ in range(self.size))) for _ in range(len(self.hash_func))]

    def get_size(self):
        if self.count <= 8:
            return "B"
        elif self.count <= 16:
            return "I"
        else:
            return "L"

    def handle_file(self, path: str) -> None:
        temp: Dict[str, int] = {}

        with open(path, "r", encoding="UTF-8") as file:
            for line in file.readlines():
                for word in line.lower().split():
                    filter_word = re.sub(PATTERN, '', word)
                    if filter_word in self.skip_words or filter_word == "":
                        continue
                    self._filter_words.append(filter_word)
                    self.add(filter_word)
                    temp.update({filter_word: self.get(filter_word)})
        word_count = list(reversed(sorted(temp.items(), key=lambda item: (item[1], item[0]))))
        result = {k: v for (k, v) in word_count[:self.frequently]}
        self._handle_result(result)

    def handle_parallel_file(self, path: str, cores: int):
        temp: Dict[str, int] = {}
        with open(path, "r", encoding="UTF-8") as file:
            raw_text = file.read().lower()
        for word in raw_text.split():
            filter_word = re.sub(PATTERN, '', word)
            if filter_word in self.skip_words:
                continue
            self._filter_words.append(filter_word)
        words_split = [self._filter_words[i::cores] for i in range(cores)]
        with mp.Pool(cores) as pool:
            result = pool.map(self._pre_parallel, words_split)
        for di in result:
            for word, count in di.items():
                if word in temp.keys():
                    temp[word] += count
                else:
                    temp[word] = count
        word_count = list(reversed(sorted(temp.items(), key=lambda item: (item[1], item[0]))))
        result = {k: v for (k, v) in word_count[:self.frequently]}
        self._handle_result(result)

    def _pre_parallel(self, data: list) -> dict:
        temp: Dict[str, int] = {}
        for word in data:
            self.add(word)
            temp.update({word: self.get(word)})
        return temp

    def _get_freq_ref(self, data: Dict[str, int]) -> dict:
        freq_ref = {k: 0 for k in data.keys()}
        for word in self._filter_words:
            if word in freq_ref.keys():
                freq_ref[word] += 1
        return freq_ref

    def _handle_result(self, data: Dict[str, int]) -> None:
        freq_ref = self._get_freq_ref(data)
        table = [('word', 'freq_ref', 'freq_approx', 'error')]
        for word, count in data.items():
            freq = freq_ref.get(word)
            err = f"{round(100 * abs(count - freq) / freq, 2)}%"
            table.append((word, freq, count, err))

        print(tabulate.tabulate(table))

        if self.ccsv:
            with open("output.csv", "w", encoding="UTF-8", newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['word', 'freq_ref', 'freq_approx', 'error'], delimiter='|')

                table.pop(0)
                for r in table:
                    writer.writerow({'word': r[0], 'freq_ref': r[1], 'freq_approx': r[2], 'error': r[3]})
                print("The result is written to a file output.csv")

        self._filter_words.clear()

    def add(self, x, value=1):
        hash_indexes = [i.get_hashed(x) for i in self.hash_func]
        for j in range(len(self.hash_func)):
            if self.backet[j][hash_indexes[j]] + value >= 2 ** self.count:  # self.count - 1
                continue
            self.backet[j][hash_indexes[j]] += value

    def get(self, x):
        hash_indexes = [i.get_hashed(x) for i in self.hash_func]
        return min([self.backet[i][hash_indexes[i]] for i in range(len(self.hash_func))])


class HashFunc:
    __slots__ = ["a", "b", "p", "buffer_size", "hasher"]

    def __init__(self, a, b, p, hash_algo=None, buffer=1000):
        self.a = a
        self.b = b
        self.p = p
        self.buffer_size = buffer
        self.hasher = hash_algo

    def get_hashed(self, text: str):
        if self.hasher:
            hashed = int(getattr(hashlib, self.hasher)(text.encode("UTF-8")).hexdigest(), 16)
        else:
            hashed = abs(hash(text))
        return ((self.a * hashed + self.b) % self.p) % self.buffer_size


def main():
    random.seed(100)
    parser: argparse.Namespace = create_parser().parse_args()
    skip_words: set = get_skip_words(parser.skip_file) if parser.skip_file else set()
    if not os.path.exists(parser.input):
        print(f"File {parser.input} no exists.")
        return exit(-1)
    hash_funcs = [
        HashFunc(random.randint(2, 1000), random.randint(2, 1000),
                 [random.choice(PRIMES) for _ in range(parser.p)][i],
                 hash_algo=parser.hash, buffer=parser.m) for i in range(parser.p)
    ]
    c = CountMinSketch(parser.k, parser.m, hash_funcs, parser.c, parser.csv, skip_words)
    if parser.parallel:
        print(f"Running in parallel mode | {mp.cpu_count()} cores")
        c.handle_parallel_file(parser.input, mp.cpu_count())
    else:
        print("Running in single mode")
        c.handle_file(parser.input)


if __name__ == '__main__':
    t0 = time.time()
    main()
    print(f"Work time script: {round(time.time() - t0, 2)} s")
