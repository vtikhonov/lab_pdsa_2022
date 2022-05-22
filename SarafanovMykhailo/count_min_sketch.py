'''
K-Top frequency with Count-Min Sketch problem implementation on Python

Author: Sarafanov Mykhailo, AI-171
'''
__all__ = ['HashFunc', 'CountMinSketch', 'read_words']

from argparse import ArgumentParser
from random import randrange as randint
from re import sub

from tabulate import tabulate

DEFAULT_BUFFER_SIZE = 1_000
skipwords = []


class HashFunc:

    def __init__(self,
                 prime_number,
                 odd_number,
                 buffer_size=DEFAULT_BUFFER_SIZE,
                 hasher=None):
        self.prime = prime_number
        self.odd = odd_number
        self.buffer_size = buffer_size
        if hasher is not None:
            self.hasher = hasher
        else:
            self.hasher = hash

    def get_hashed(self, text):
        hash_val = self.hasher(text)
        if (hash_val < 0):
            hash_val = abs(hash_val)
        return ((((
            (hash_val % self.buffer_size) * self.prime) % self.buffer_size) *
                 self.odd) % self.buffer_size)

    @staticmethod
    def randomize(buffer_size=DEFAULT_BUFFER_SIZE, hasher=None):
        return HashFunc(randint(100), randint(100), buffer_size, hasher)


class CountMinSketch():

    def __init__(self,
                 hash_funcs,
                 buffer_size=DEFAULT_BUFFER_SIZE,
                 input_words=[]):
        self.hash_funcs = hash_funcs
        self.buffer_size = buffer_size
        if input_words:
            self.fill_sketch(input_words)
        else:
            self.sketch = [0 for _ in enumerate(self.hash_funcs)]
            self.frequences = []

    def fill_sketch(self, input_words):
        self.sketch = [[0 for _ in range(self.buffer_size)]
                       for __ in enumerate(self.hash_funcs)]
        self.frequences = []
        for word in input_words:
            hashes = [x.get_hashed(word) for x in self.hash_funcs]
            for x, _ in enumerate(self.hash_funcs):
                self.sketch[x][hashes[x]] += 1
                if [min(hashes), word] not in self.frequences:
                    self.frequences.append([min(hashes), word])
        self.frequences.sort()

    def get_top(self, n):
        return self.frequences[-n:]


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
    args_parser.add_argument('--output', type=str, required=False)
    return args_parser.parse_args()


if __name__ == '__main__':
    params = __process_args()
    __init_skipwords('./skip_words.txt')
    input_words = read_words(params.input)
    hash_funcs = [HashFunc.randomize() for _ in range(params.p)]

    count_min_sketch = CountMinSketch(hash_funcs,
                                      buffer_size=params.m,
                                      input_words=input_words)
    top_k_words = count_min_sketch.get_top(params.k)
    print(f'Top {params.k} words:')
    top_k_words_table = tabulate(top_k_words)
    print(top_k_words_table)

    if params.output:
        with open(params.output, 'w') as output_file:
            output_file.write(top_k_words_table)
        print(f'Written to {params.output}')
