from typing import Dict
import argparse
import hashlib
import random
import array
import re


# PRIMES = (3, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281, 3217, 1281, 4423, 9689, 9941, 11213, 19937, 21701)  # простые числа Мерсенна
PRIMES = (7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535, 131071, 262143, 524287, 1048575, 2097151)


def commline_parsing():  # создание агрументов для парсинга командной строки
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation | Частота K-Top с реализацией задачи Count-Min Sketch')
    parser.add_argument('--input', type=str, help='Исходный файл', required=True)
    parser.add_argument('-k', type=int, help='Количество наиболее частых элементов, которые необходимо вывести', required=True)
    parser.add_argument('-m', type=int, help='Размер буфера алгоритма Count-Min Sketch', required=True)
    parser.add_argument('-p', type=int, help='Количество независимых хеш-функций', required=True)
    parser.add_argument('-c', type=int, default=12, help='Количество бит на счетчик, по умолчанию 12', required=True)
    parser.add_argument('--hash', type=str, help='Хеш-алгоритм', required=True)
    return parser

def get_allwords(path: str, skip_words: set):
    all_words = []
    with open(path, "r", encoding="UTF-8") as file:
        for line in file.readlines():
            for word in line.lower().split():
                temp_word = re.sub(r'[.,?!/|\[\]\\"“\t\n)(:;#&\']', '', word).replace("﻿", "")
                if temp_word not in skip_words and temp_word != "":
                    all_words.append(temp_word)
    return all_words


class CountMinSketch:

    def __init__(self, k, m, p, c, allwords, skip_words=None):
        self.k = k  # кол-во наиб. частых элементов
        self.m = m  # кол-во столбцов матрицы (размерность хеш-функций)
        self.p = p  # кол-во хеш-функций
        self.c = c  # битовый счетчик
        self.skip_words = skip_words
        self.words_dict: Dict[str, int] = {}
        self.M = [array.array(self.get_size(), (0 for _ in range(self.m))) for _ in range(len(self.p))]
        self.allwords = allwords

    def get_size(self):
        if self.c <= 8:
            return "B"
        elif self.c <= 16:
            return "I"
        else:
            return "L"

    def fill_M(self):  # заполнение словаря и матрицы значениями
        for temp_word in self.allwords:
            self.add(temp_word)
            if len(self.words_dict) < self.k:
                self.words_dict.update({temp_word: self.frequency(temp_word)})
            else:
                temp_words_dict = self.words_dict.copy()
                if temp_word in temp_words_dict.keys():
                    self.words_dict.update({temp_word: self.frequency(temp_word)})
                elif self.frequency(temp_word) >= min(temp_words_dict.values()):
                    self.words_dict = dict(sorted(self.words_dict.items(), key=lambda x: x[1], reverse=True))
                    self.words_dict.popitem()
                    self.words_dict.update({temp_word: self.frequency(temp_word)})

    def add(self, x, delta=1):  # добавление чисел в матрицу
        hash_indexes = [i.get_hashfunc_family(x) for i in self.p]
        for j in range(len(self.p)):
            if self.M[j][hash_indexes[j]] < (2 ** self.c - delta):
                self.M[j][hash_indexes[j]] += delta  # +1

    def frequency(self, x):  # поиск частоты элементов
        hash_indexes = [i.get_hashfunc_family(x) for i in self.p]
        result = []
        for i in range(len(self.p)):
            result.append(self.M[i][hash_indexes[i]])
        return min(result)


class HashFunction:
    def __init__(self, a, b, p, buff, hash_algo=None):
        self.a = a
        self.b = b
        self.p = p
        self.buffer_size = buff
        self.hasher = hash_algo

    def get_hashfunc_family(self, text: str):  # создание семейства p хеш-функций
        if self.hasher:
            reference = getattr(hashlib, self.hasher)
            hashed = int(reference(text.encode("UTF-8")).hexdigest(), 16)
        else:
            hashed = abs(hash(text))
        return ((self.a * hashed + self.b) % self.p) % self.buffer_size


def main():
    random.seed(50)
    skip_words = set()
    hash_funcs = set()
    parser = commline_parsing().parse_args()
    with open("skip_words.txt", "r") as skip_file:
        for line in skip_file.readlines():
            skip_words.add(line.rstrip("\n"))

    primes = []
    k = 0
    while k < parser.p:
        p_temp = random.choice(PRIMES)
        if p_temp >= parser.m:
            primes.append(p_temp)
            k += 1

    for i in range(parser.p):
        hash_funcs.add(HashFunction(random.randint(2, 1000), random.randint(2, 1000), primes[i], parser.m, hash_algo = parser.hash))

    all_words = get_allwords(parser.input, skip_words)
    cms = CountMinSketch(parser.k, parser.m, hash_funcs, parser.c, all_words, skip_words)
    cms.fill_M()

    for i in cms.words_dict.items():
        # print("Слово: " + "' " + i[0] + " '")
        # print("Вероятностная частота: ", i[1])
        print(f"Слово: ' {i[0]} '")
        print(f"Вероятностная частота: {i[1]}")
        count = 0
        for j in all_words:
            if i[0] == j:
                count += 1
        print(f"Реальная частота: {count}")
        print(f"Ошибка (%): {float('{:.3f}'.format(abs(100 * ((count - i[1]) / i[1]))))}")


main()
