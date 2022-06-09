'''
K-Top frequency problem with Count-Min Sketch implementation on Python

This script implementes Count-Min Sketch algorithm for solving problem of
getting top K frequent words in the datasteam.

You can import class for your own usage or use this script. You can use the
following cmd flags for test:
--input path to input file with words
-k number of top elements to find
-p number of independent hash funcs to use. Functions are being created with
    randomized args
-m buffer size for all possible options. Defaults to 1000
--parallel run in parrallel mode using Python mulltiprocessing. All available
    cores will be used
--output path where top K words will be saved. Words will be printed on stdout
    anyway.

Please note that some words will be skipped. The list of words to skip is in
the skip_words.txt file

Author: Sarafanov Mykhailo, AI-171
'''
__all__ = ['HashFunc', 'HasherError', 'CountMinSketch', 'read_words']

import hashlib
from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool, cpu_count
from random import randint, seed
from re import sub
from time import time

from tabulate import tabulate

DEFAULT_BUFFER_SIZE = 1_000
skipwords = []


class HasherError(Exception):
    pass


class CountMinSketchError(Exception):
    pass


class HashFunc:

    def __init__(self,
                 a,
                 b,
                 p,
                 buffer_size=DEFAULT_BUFFER_SIZE,
                 hash_algo=None):
        """
        Custom hashing function from family class. Uses implementation of hash
        functions family proposed by Lawrence Carter and Mark Wegman.

        Args:
            a (int): some random int
            b (int): some random int
            p (int): Merces prime (2**k - 1)
            buffer_size (int, optional): buffer size to limit hashvalue.
                Defaults to DEFAULT_BUFFER_SIZE.
            hash_algo (str, optional): hashing algorithm from hashlib to use as
                base hasher. Python's default hash() is used if not specified.
        """
        self.a = a
        self.b = b
        self.p = p
        self.buffer_size = buffer_size
        if hash_algo is not None:
            self.hasher = HashFunc.__get_hashlib_hasher(hash_algo)
        else:
            self.hasher = hash

    def get_hashed(self, text):
        hashed = abs(self.hasher(text))
        return (((self.a * hashed + self.b) % self.p) % self.buffer_size)

    @staticmethod
    def __get_hashlib_hasher(hasher_name):
        if hasher_name not in hashlib.algorithms_guaranteed:
            raise HasherError(f'Algorithm {hasher_name} is not implemented')
        hashlib_func = getattr(hashlib, hasher_name)

        def get_hashed(text):
            hashed = hashlib_func(text.encode('utf-8')).hexdigest()
            return int(hashed, 16)

        return get_hashed


class CountMinSketch():

    def __init__(self,
                 hash_funcs,
                 k_count,
                 input_words=[],
                 buffer_size=DEFAULT_BUFFER_SIZE):
        self.hash_funcs = hash_funcs
        if not k_count:
            raise CountMinSketchError('Top k count must be specified')
        self.k_count = k_count
        self.buffer_size = buffer_size
        if input_words:
            self.fill_sketch(input_words)
        else:
            self.sketch = [0 for _ in enumerate(self.hash_funcs)]
            self.frequences = {}

    def fill_sketch(self, input_words):
        self.sketch = [[0 for _ in range(self.buffer_size)]
                       for __ in enumerate(self.hash_funcs)]
        self.frequences = {}
        for word in input_words:
            hashes = [x.get_hashed(word) for x in self.hash_funcs]
            counts = []
            for x, _ in enumerate(self.hash_funcs):
                self.sketch[x][hashes[x]] += 1
                counts.append(self.sketch[x][hashes[x]])
            min_hash_cnt = min(counts)
            present = (word in self.frequences.keys())
            if ((present and self.frequences[word] < min_hash_cnt)
                    or (not present)):
                self.frequences[word] = min_hash_cnt
            if len(self.frequences) > self.k_count:
                self.frequences = CountMinSketch.sort_dict(self.frequences)
                self.frequences.popitem()

    @staticmethod
    def sort_dict(dct):
        return {k: v for k, v in sorted(dct.items(), key=lambda x: x[1], reverse=True)}


def __get_mercen_primes(n):
    primes = []
    for _ in range(n):
        primes.append(2**randint(2, 10) - 1)
    return primes


def __init_skipwords(skipwords_path):
    with open(skipwords_path, 'r') as skip_words_file:
        for word in skip_words_file.read().split():
            skipwords.append(word)


def read_words(filepath):
    filtered_words = []
    with open(filepath, 'r', encoding='utf8') as text_file:
        input_text = text_file.read().lower()
    for word in input_text.split():
        word = sub("[':;,.!?“”_]", '', word)
        if skipwords and word not in skipwords:
            filtered_words.append(word)
    return filtered_words


def __process_args():
    args_parser = ArgumentParser(description='Set params')
    args_parser.add_argument('--input',
                             type=str,
                             required=True,
                             help='path to file or folder with a textual file')
    args_parser.add_argument('-k',
                             type=int,
                             required=True,
                             help='number of top frequent element')
    args_parser.add_argument('-p',
                             type=int,
                             required=True,
                             help='number of independent hash functions')
    args_parser.add_argument('-m',
                             type=int,
                             required=False,
                             help='buffer size. Defaults to ' +
                             str(DEFAULT_BUFFER_SIZE),
                             default=DEFAULT_BUFFER_SIZE)
    args_parser.add_argument('--parallel',
                             action='store_true',
                             help=('running in parallel mode using '
                                   'multiprocessing. Disabled by defaut'),
                             default=False)
    args_parser.add_argument('--output', type=str, required=False)
    return args_parser.parse_args()


def __get_frequences(words_chunk, hash_funcs, k_count, buffer_size):
    return CountMinSketch(hash_funcs, k_count, words_chunk, buffer_size).frequences


def __merge_frequences(frequences):
    merged = {}
    for freqs_chunk in frequences:
        for word, hashes_cnt in freqs_chunk.items():
            if word in merged.keys():
                merged[word] += hashes_cnt
            else:
                merged[word] = hashes_cnt
    return merged


if __name__ == '__main__':
    seed(1000)
    params = __process_args()
    __init_skipwords('./skip_words.txt')
    input_words = read_words(params.input)
    primes = __get_mercen_primes(params.p)
    hash_funcs = [
        HashFunc(randint(2, 1000), randint(2, 1000), primes[i])
        for i in range(params.p)
    ]

    top_k_words = None
    start_time = time()
    if params.parallel:
        cpus = cpu_count()
        print(f'Running in parallel mode (using {cpus} cpus)')
        words_split = [input_words[i::cpus] for i in range(0, cpus)]

        with Pool(cpus) as pool:
            packed_func = partial(__get_frequences,
                                  hash_funcs=hash_funcs,
                                  k_count=params.k,
                                  buffer_size=params.m)
            freqs = pool.map(packed_func, words_split)
        merged_freqs = __merge_frequences(freqs)
        top_k_words = list(CountMinSketch.sort_dict(merged_freqs).items())[:params.k]
    else:
        print('Running in single-thread mode')
        count_min_sketch = CountMinSketch(hash_funcs,
                                          params.k,
                                          input_words=input_words,
                                          buffer_size=params.m)
        top_k_words = list(count_min_sketch.frequences.items())
    exec_time = time() - start_time
    print(f'Top {params.k} words:')
    top_k_words_table = tabulate(top_k_words)
    print(top_k_words_table)
    print(f'Calculation time: {round(exec_time)}s')

    if params.output:
        with open(params.output, 'w') as output_file:
            output_file.write(top_k_words_table)
        print(f'Written to {params.output}')
