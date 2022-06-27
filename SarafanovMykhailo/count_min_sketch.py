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
-m cell size for liming counter cell size in bits. Defaults to 12. Will be used
    for selecting sketch array dtype
--silent do not raise exception if counter exceeds cell limit in bits. False by
    default
--parallel run in parrallel mode using Python mulltiprocessing. All available
    cores will be used
--hash hash algorithm to use as base. Python's default hash will be used if not
    specified
--output path where top K words will be saved. Words will be printed on stdout
    anyway.

Please note that some words will be skipped. The list of words to skip is in
the skip_words.txt file

Author: Sarafanov Mykhailo, AI-171
'''
__all__ = [
    'HashFunc', 'HasherError', 'CountMinSketch', 'CountMinSketchError',
    'read_words'
]

import hashlib
from argparse import ArgumentParser
from warnings import warn as print_warning
from functools import partial
from multiprocessing import Pool, cpu_count
from random import randint, seed, choice
from re import sub
from time import time

from numpy import uint8, uint16, uint32, uint64, zeros
from tabulate import tabulate

DEFAULT_BUFFER_SIZE = 1_000
DEFAULT_CELL_SIZE = 12
MERCEN_PRIMES = (7, 31, 127, 2047, 8191, 131071, 524287, 8388607, 536870911,
                 2147483647)
skipwords = []


class HasherError(Exception):
    pass


class CountMinSketchError(Exception):
    pass


class HashFunc:
    '''
    Custom hashing function from family class.

    Uses implementation of hash functions family proposed by Lawrence Carter
    and Mark Wegman.
    '''
    def __init__(self,
                 a,
                 b,
                 p,
                 buffer_size=DEFAULT_BUFFER_SIZE,
                 hash_algo=None):
        '''
        Args:
            a (int): some random int
            b (int): some random int
            p (int): Merces prime (2**k - 1)
            buffer_size (int, optional): buffer size to limit hashvalue.
                Defaults to DEFAULT_BUFFER_SIZE.
            hash_algo (str, optional): hashing algorithm from hashlib to use as
                base hasher. Python's default hash() is used if not specified.
        '''
        self.a = a
        self.b = b
        self.p = p
        self.buffer_size = buffer_size
        if hash_algo is not None:
            self.__custom_hasher = HashFunc.__get_hashlib_hasher(hash_algo)
        else:
            self.__custom_hasher = None

    def get_hashed(self, text):
        if self.__custom_hasher is None:
            hashed = abs(hash(text))
        else:
            hashed_hex = self.__custom_hasher(text.encode('utf-8')).hexdigest()
            hashed = int(hashed_hex, 16)
        return (((self.a * hashed + self.b) % self.p) % self.buffer_size)

    @staticmethod
    def __get_hashlib_hasher(hasher_name):
        if hasher_name not in hashlib.algorithms_guaranteed:
            raise HasherError(f'Algorithm {hasher_name} is not implemented')
        return getattr(hashlib, hasher_name)


class CountMinSketch():
    '''
    CountMinSketch implementation for solving top K frequent problem.

    Uses numpy array for sketch storing. Memory usage is being limited by
    setting buffer size and cell size. Counter type is being selected on cell
    size limit (in bits). Freqeunces dict is being limited, so k value must
    be specified. For running algorithm simply add input words or call
    fill_sketch providing text sequence.
    '''
    def __init__(self,
                 hash_funcs,
                 k_count,
                 input_words=[],
                 cell_size=DEFAULT_CELL_SIZE,
                 buffer_size=DEFAULT_BUFFER_SIZE,
                 silent=False):
        '''
        Args:
            hash_funcs (list): list containing family of hash functions to get
                hash values for words
            k_count (int): how many top frequent words should be tracked
            input_words (list): input text sequence to process. Defaults to
                empty list. If not provided - fill_sketch can be called later
            cell_size (int): counter cell limit (in bits). Will be used when
                determining sketch data type. CountMinSketchError will be
                raised if value exceeds defined cell_size. Defaults to
                DEFAULT_CELL_SIZE
            buffer_size (int): sketch buffer size. Must be limited to max hash
                value. Defaults to DEFAULT_BUFFER_SIZE
            silent (bool): do not raise exception, but print warning if counter
                exceeds cell size limit. Defaults to False (meaning that
                exception will be raised)
        '''
        self.hash_funcs = hash_funcs
        if not k_count:
            raise CountMinSketchError('Top k count must be specified')
        self.k_count = k_count
        self.buffer_size = buffer_size
        self.cell_size = cell_size
        if cell_size <= 8:
            cell_type = uint8
        elif cell_size <= 16:
            cell_type = uint16
        elif cell_size <= 32:
            cell_type = uint32
        elif cell_size <= 64:
            cell_type = uint64
        else:
            raise CountMinSketchError(f'Cells of {cell_size} bits are not '
                                      'supported')
        self.__silent = silent
        self.sketch = zeros(shape=(len(self.hash_funcs), self.buffer_size),
                            dtype=cell_type)
        self.frequences = {}
        if input_words:
            self.fill_sketch(input_words)

    def fill_sketch(self, input_words):
        for word in input_words:
            hashes = [x.get_hashed(word) for x in self.hash_funcs]
            counts = []
            for x, _ in enumerate(self.hash_funcs):
                cnt_updated = self.sketch[x][hashes[x]] + 1
                if cnt_updated >= 2**self.cell_size:
                    log_msg = (f'Counter exceeds cell limit: {self.cell_size} '
                               'bits')
                    if self.__silent:
                        print_warning(log_msg)
                    else:
                        raise CountMinSketchError(log_msg)
                else:
                    self.sketch[x][hashes[x]] = cnt_updated
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
        return {
            k: v
            for k, v in sorted(dct.items(), key=lambda x: x[1], reverse=True)
        }


def __get_mercen_primes(n, buffer_size):
    primes = []
    to_select = [x for x in MERCEN_PRIMES if x > buffer_size]
    for _ in range(n):
        primes.append(choice(to_select))
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
                             help='path to file or folder with a text file')
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
    args_parser.add_argument('--hash',
                             type=str,
                             required=False,
                             help='custom hash algorithm to use as base for ' +
                             'creating hashfuncs family. Supported: ' +
                             ', '.join(hashlib.algorithms_guaranteed) +
                             '. Python hash is used by default')
    args_parser.add_argument('-c',
                             type=int,
                             required=False,
                             default=DEFAULT_CELL_SIZE,
                             help='Counter bits size limit. Defaults to ' +
                             str(DEFAULT_CELL_SIZE))
    args_parser.add_argument('--silent',
                             action='store_true',
                             required=False,
                             default=False,
                             help='Do not raise exception if counter exceeds '
                             'bits size limit')
    args_parser.add_argument('--output',
                             type=str,
                             required=False,
                             help='path to file to write top k words')
    return args_parser.parse_args()


def __get_frequences(words_chunk, hash_funcs, k_count, cell_size, buffer_size,
                     silent):
    return CountMinSketch(hash_funcs, k_count, words_chunk, cell_size,
                          buffer_size, silent).frequences


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
    if params.m > max(MERCEN_PRIMES):
        raise HasherError(f'Buffer size {params.m} is too high')

    primes = __get_mercen_primes(params.p, params.m)
    hash_funcs = [
        HashFunc(randint(2, 1000),
                 randint(2, 1000),
                 primes[i],
                 hash_algo=params.hash,
                 buffer_size=params.m) for i in range(params.p)
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
                                  cell_size=params.c,
                                  buffer_size=params.m,
                                  silent=params.silent)
            freqs = pool.map(packed_func, words_split)
        merged_freqs = __merge_frequences(freqs)
        top_k_words = list(CountMinSketch.sort_dict(merged_freqs).items())[:params.k]
    else:
        print('Running in single-thread mode')
        count_min_sketch = CountMinSketch(hash_funcs,
                                          params.k,
                                          input_words=input_words,
                                          cell_size=params.c,
                                          buffer_size=params.m,
                                          silent=params.silent)
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

    prob_freqs = {k: v for (k, v) in top_k_words}
    real_freqs = {k: 0 for k in prob_freqs.keys()}
    for word in input_words:
        if word in real_freqs.keys():
            real_freqs[word] += 1

    err_tbl = [('word', 'freq_ref', 'freq_approx', 'error')]
    for word, freq_approx in prob_freqs.items():
        freq_ref = real_freqs[word]
        err = 100. * abs(freq_approx - freq_ref) / freq_ref
        err_tbl.append((word, freq_ref, freq_approx, str(round(err, 2)) + '%'))
    print('\nError calculation:')
    print(tabulate(err_tbl))
