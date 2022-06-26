from typing import Dict
import argparse
import hashlib
import random
import array
import re


PRIMES = (1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535, 131071, 262143, 524287, 1048575, 2097151)  # простые числа Мерсенна


def commline_parsing():  # создание агрументов для парсинга командной строки
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation | Частота K-Top с реализацией задачи Count-Min Sketch')
    parser.add_argument('-k', type=int, help='Количество наиболее частых элементов, которые необходимо вывести', required=True)
    parser.add_argument('-m', type=int, help='Размер буфера алгоритма Count-Min Sketch', required=True)
    parser.add_argument('-p', type=int, help='Количество независимых хеш-функций', required=True)
    parser.add_argument('-c', type=int, default=12, help='Количество бит на счетчик, по умолчанию 12', required=True)
    return parser


class CountMinSketch:

    def __init__(self, k, m, p, c, skip_words=None):
        self.k = k  # кол-во наиб. частых элементов
        self.m = m  # кол-во столбцов матрицы (размерность хеш-функций)
        self.p = p  # кол-во хеш-функций
        self.c = c  # битовый счетчик
        self.skip_words = skip_words
        self.words_dict: Dict[str, int] = {}
        self.M = [array.array(self.get_size(), (0 for _ in range(self.m))) for _ in range(len(self.p))]

    def get_size(self):
        if self.c <= 8:
            return "B"
        elif self.c <= 16:
            return "I"
        else:
            return "L"

    def fill_M(self, path: str):  # заполнение словаря и матрицы значениями
        with open(path, "r", encoding="UTF-8") as file:
            for line in file.readlines():
                if line not in self.skip_words:
                    for word in line.split(" "):
                        temp_word = re.sub(r'[.,?!/|[\]\\"“\t\n)(:;#&\']', '', word.lower())
                        if temp_word == "" or temp_word in self.skip_words:
                            continue
                        self.add(temp_word)
                        self.words_dict.update({temp_word: self.frequency(temp_word)})

    def add(self, x, delta=1):  # добавление чисел в матрицу
        hash_indexes = [i.get_hashfunc_family(x) for i in self.p]
        for j in range(len(self.p)):
            self.M[j][hash_indexes[j]] += delta  # +1

    def frequency(self, x):  # поиск частоты элементов
        hash_indexes = [i.get_hashfunc_family(x) for i in self.p]
        result = []
        for i in range(len(self.p)):
            result.append(self.M[i][hash_indexes[i]])
        return min(result)

    def get(self, word: str):  # вывод на экран частоты конкретного слова (при необходимости)
        print(self.words_dict.get(word))


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
    random.seed(15)
    skip_words = []
    hash_funcs = []
    parser = commline_parsing().parse_args()
    with open("skip_words_new.txt", "r") as skip_file:
        for line in skip_file.readlines():
            skip_words.append(line.rstrip("\n"))

    primes = [random.choice(PRIMES) for _ in range(parser.p)]

    for i in range(parser.p):
        hash_funcs.append(HashFunction(random.randint(2, 1000), random.randint(2, 1000), primes[i], parser.m, hash_algo="md5"))

    cms = CountMinSketch(parser.k, parser.m, hash_funcs, parser.c, skip_words)
    cms.fill_M("Oliver_Twist.txt")

    sorted_cortege = sorted(cms.words_dict.items(), key = lambda x: x[1], reverse=True)  # отсортированный по убыванию список кортежей

    for i in range(parser.k):
        print("Слово: " + "' " + sorted_cortege[i][0] + " '")
        print("Вероятностная частота: ", sorted_cortege[i][1])
        count = 0
        with open("Oliver_Twist.txt", "r", encoding="UTF-8") as file:
            for line in file.readlines():
                for word in line.split(" "):
                    temp_word = re.sub(r'[.,?!/|[\]\\"“\t\n)(:;#&\']', '', word.lower())
                    if sorted_cortege[i][0] == temp_word:
                        count += 1
        print("Реальная частота: ", count)
        print("Ошибка (%): ", float('{:.3f}'.format(abs(100 * ((count - sorted_cortege[i][1]) / sorted_cortege[i][1])))))


main()
