import multiprocessing as mp
import argparse
import hashlib
import typing
import array
import time
import csv
import io
import os
import re


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


def get_skip_words(file: io.FileIO) -> list:
    return [line.strip() for line in file.readlines()]


class CountMinSketchParser:
    __slots__ = ["frequently", "size", "hash_func", "count", "algorithm", "skip_words", "ccsv", "backet"]

    def __init__(self, frequently, size, hash_func, count, algorithm, ccsv=None, skip_words=None):
        self.frequently = frequently  # k
        self.size = size  # m
        self.hash_func = hash_func  # p
        self.count = count  # c
        self.algorithm = algorithm
        self.skip_words = skip_words
        self.ccsv = ccsv
        self.backet = [array.array(self.get_size(), (0 for _ in range(self.size))) for _ in range(self.hash_func)]

    def bitint(self, number: int, bit=False):
        """Реализовал чуть-чуть проще, без сдвигов и логических операций. Это даст небольшую задержку по
        сравнению с логическим операциями, но результат от этого не меняется.
        """
        bits = format(number, "b")
        result = "0" * (self.count - len(bits)) + bits
        if len(result) > self.count:
            raise ValueError(
                f"Amount bit ({len(result)}) in number {int(result, 2)}: b{result} exceeded the specified "
                f"value ({self.count}) of bits.")
        return result if bit else int(result, 2)

    def get_size(self):
        if self.count <= 8:
            return "B"
        elif self.count <= 16:
            return "I"
        else:
            return "L"

    def handle_file(self, path: str):
        temp: typing.Dict[str, int] = {}
        with open(path, "r", encoding="UTF-8") as file:
            for line in file.readlines():
                if line not in self.skip_words:
                    for word in line.split(" "):
                        filter_word = re.sub(r'[(),.:;!?\n\t\'\\[\]"]', '', word)
                        if filter_word == "" or filter_word in self.skip_words:
                            continue
                        self.add(filter_word)
                        if not temp.get(filter_word):
                            temp.update({filter_word: self.get(filter_word)})

        word_count = reversed(sorted(temp.items(), key=lambda item: (item[1], item[0])))
        if self.ccsv:
            with open("output.csv", "w", encoding="UTF-8", newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['word', 'freq_ref'])
                for _ in word_count:
                    writer.writerow({'word': _[0], 'freq_ref': _[1]})
                print("The result is written to a file output.csv")
        else:
            for _ in word_count:
                print(f"word: {_[0]} | freq_ref: {_[1]}")

        print("*" * 20)
        for k, v in temp.items():
            if v == self.frequently:
                print(f"Element with frequently {self.frequently}: {k}")
        temp.clear()

    def my_hash(self, line):
        if self.algorithm:
            code = hashlib.new(self.algorithm)
            code.update(line.encode("UTF-8"))
            return int(code.hexdigest(), 16) % self.size
        else:
            code = str(hash(line)).encode("UTF-8")
            return int(code, 16) % self.size

    def add(self, x, value=1):
        hash_index = self.my_hash(x)
        for i in range(len(self.backet)):
            self.backet[i][hash_index] += value
            self.bitint(self.backet[i][hash_index])

    def get(self, x):
        hash_index = self.my_hash(x)
        return min(self.backet[i][hash_index] for i in range(len(self.backet)))


def main():
    parser: argparse.Namespace = create_parser().parse_args()
    skip_words: list = get_skip_words(parser.skip_file) if parser.skip_file else []

    if not os.path.exists(parser.input):
        return print(f"File {parser.input} no exists.")

    c = CountMinSketchParser(parser.k, parser.m, parser.p, parser.c, parser.hash, parser.csv, skip_words)
    c.handle_file(parser.input)


if __name__ == '__main__':
    t0 = time.time()
    main()
    print(f"Work time script: {round(time.time() - t0, 2)} s")