# -*- coding: utf-8 -*-
from typing import Dict
import pandas as pd
import numpy as np
import argparse
import array
import re

PRIMES = (7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279, 2203, 2281, 3217, 1281, 4423, 9689, 9941, 11213, 19937, 21701)  # простые числа Мерсенна
SEPARATORS = re.compile(r'[(\ ),.:;!?\n\t\'\\[\]"”“]')
DELTA = 0.02
EPSILON = 0.005


def pyParsing():  # создание агрументов для парсинга командной строки
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation')
    parser.add_argument('--input', type=str, help='Path to file or folder with a textual file', required=False, default='Anne of Green Gables by L. M. Montgomery (8593).txt')
    parser.add_argument('-k', type=int, help='Number of top frequent element that we are looking for.', required=False, default=10)
    parser.add_argument('-m', type=int, help='Count-min sketch buffer size', required=False, default=int(np.e / EPSILON))  # w
    parser.add_argument('-p', type=int, help='Number of independent hash functions', required=False, default=int(np.log(1 / DELTA)))  # d
    parser.add_argument('-c', type=int, help='Number of bits per counter, default is 12', required=False, default=12)
    return parser


class CountMinSketch:

    def __init__(self, k, m, p, c, skip_words=None):
        self.k = k  # кол-во наиб. частых элементов
        self.m = m  # w - кол-во столбцов матрицы (размерность хеш-функций)
        self.p = p  # d - кол-во хеш-функций
        self.c = c  # битовый счетчик
        self.skip_words = skip_words
        self.words_dict: Dict[str, int] = {}  # словарь ключ-значение
        self.M = [array.array(self.getSize(), (0 for _ in range(self.m))) for _ in range(self.p)]

    def getSize(self):
        if self.c <= 8:
            return "B"
        elif self.c <= 16:
            return "I"
        else:
            return "L"

    def updateCMSketch(self, data, cMSketch):
        for w in data:
            for j in range(p):
                i = hash(w + str(j)) % m
                cMSketch[j, i] += 1
        return cMSketch

    def frequencyApprox(self, data, cMSketch):
        f_dict = {}
        for w_n, w in enumerate(data):
            f = []
            for j in range(self.p):
                i = hash(w + str(j)) % self.m
                f.append(cMSketch[j, i])
            f_dict[w] = min(f)
        sorted_freq = sorted(f_dict.items(), key=lambda item: int(item[1]), reverse=True)
        return sorted_freq

    def frequencyRef(self, data):
        freq = {}
        for w in data:
            if w not in freq.keys():
                freq[w] = 1
            else:
                freq[w] += 1
        sorted_freq = sorted(freq.items(), key=lambda item: int(item[1]), reverse=True)
        return sorted_freq

    def getResult(self, freq_approx, freq_ref):
        result = dict(freq_ref[:self.k])
        df = pd.DataFrame({'word': list(result.keys()), 'freq_ref': list(result.values())})
        freq_approx = dict(freq_approx)
        freq_approx_res = []
        for w in result.keys():
            freq_approx_res.append(int(freq_approx[w]))
        df.insert(2, 'freq_approx', freq_approx_res, True)
        error = []

        freq_ref_res = result.values()
        for ref, approx in zip(freq_ref_res, freq_approx_res):
            error.append(100 * abs(approx - ref) / ref)
        df.insert(3, 'error', error, True)
        return df


parser = pyParsing().parse_args()
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

skipWords = []
with open("skip_words.txt", "r") as skipFile:
    for line in skipFile.readlines():
        skipWords.append(line.rstrip("\n"))

countMinSketch = CountMinSketch(k, m, p, c, skipWords)
cMSketch = np.zeros((p, m))

allText = []
with open(input, "r", encoding="UTF-8-sig") as openFile:
    for line in openFile.readlines():
        if line not in skipWords:
            for word in line.split():
                text = re.sub(SEPARATORS, "", word.lower())
                if text == "" or text in skipWords:
                    continue
                allText.append(text)

cMSketch = countMinSketch.updateCMSketch(allText, cMSketch)
freq_approx = countMinSketch.frequencyApprox(allText, cMSketch)
freq_ref = countMinSketch.frequencyRef(allText)

# print result
result = countMinSketch.getResult(freq_approx, freq_ref)
print(result)

open('result.txt', 'w').write(result.to_string())
