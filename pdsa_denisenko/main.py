# -*- coding: utf-8 -*-
from typing import Dict
import pandas as pd
import numpy as np
import argparse
import re

SEPARATORS = re.compile(r'[(\s),.:;!?\n\t\'\\[\]"”“]')
DELTA = 0.02
EPSILON = 0.005


def pyParsing():  # создание агрументов для парсинга командной строки
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation')
    parser.add_argument('--input', type=str, help='Path to file or folder with a textual file', required=False, default='Anne of Green Gables by L. M. Montgomery (8593).txt')
    parser.add_argument('-k', type=int, help='Number of top frequent element that we are looking for.', required=False, default=10)
    parser.add_argument('-m', type=int, help='Count-min sketch buffer size', required=False, default=int(np.e / EPSILON))
    parser.add_argument('-p', type=int, help='Number of independent hash functions', required=False, default=int(np.log(1 / DELTA)))
    parser.add_argument('-c', type=int, help='Number of bits per counter, default is 12', required=False, default=12)
    return parser


class CountMinSketch:

    def __init__(self, k, m, p, c, skip_words=None):
        self.k = k  # кол-во наиб. частых элементов
        self.m = m  # w - кол-во столбцов матрицы (размерность хеш-функций)
        self.p = p  # d - кол-во хеш-функций
        self.c = c  # битовый счетчик
        self.cMSketch = np.zeros((p, m), dtype=self.getSize())
        self.skip_words = skip_words
        self.words_dict: Dict[str, int] = {}  # словарь ключ-значение

    def getSize(self):
        if self.c <= 8:
            return "B"
        elif self.c <= 16:
            return "H"
        elif self.c <= 32:
            return "I"
        else:
            return "L"

    def updateCMSketch(self, data):
        for x in data:
            for j in range(pUser):
                i = hash(x + str(j)) % self.m
                self.cMSketch[j, i] += 1

    def frequencyEstimation(self, x):
        f = []
        for j in range(self.p):
            i = int(hash(x + str(j))) % self.m
            f.append(self.cMSketch[j, i])
        return min(f)

    def kTopElements(self, data):
        X = []
        for x in data:
            if x in X:
                continue
            if len(X) < self.k:
                X.append(x)
            else:
                f = self.frequencyEstimation(x)
                X_f = {x: self.frequencyEstimation(x) for x in X}
                x_min = min(X_f, key=X_f.get)
                f_min = X_f[x_min]
                if f > f_min:
                    X.remove(x_min)
                    X.append(x)
        return X

    def frequencyRef(self, data):
        freq = {}
        for x in data:
            if x not in freq.keys():
                freq[x] = 1
            else:
                freq[x] += 1
        sorted_freq = sorted(freq.items(), key=lambda item: int(item[1]), reverse=True)
        return sorted_freq[:self.k]

    @staticmethod
    def getResult(freqApprox, freqRef):
        freqRefResult = dict(freqRef)
        freqApproxRes = []
        for x in freqRefResult.keys():
            freqApproxRes.append(int(dict(freqApprox)[x]))

        error = []
        for ref, approx in zip(freqRefResult.values(), freqApproxRes):
            error.append(100 * abs(approx - ref) / ref)

        df = pd.DataFrame({'word': list(freqRefResult.keys()), 'freqRef': list(freqRefResult.values())})
        df.insert(2, 'freqApprox', freqApproxRes, True)
        df.insert(3, 'error', error, True)
        return df


userParser = pyParsing().parse_args()
inputPath = userParser.input
kUser = userParser.k
mUser = userParser.m
pUser = userParser.p
cUser = userParser.c
print('inputPath: ', inputPath)
print('k:', kUser)
print('m: ', mUser)
print('p: ', pUser)
print('c: ', cUser)

skipWords = []
with open("skip_words.txt", "r") as skipFile:
    try:
        for line in skipFile.readlines():
            skipWords.append(line.rstrip("\n"))
    finally:
        skipFile.close()

allText = []
with open(inputPath, "r", encoding="UTF-8-sig") as openFile:
    try:
        for line in openFile.readlines():
            if line not in skipWords:
                for word in line.split():
                    text = re.sub(SEPARATORS, "", word.lower())
                    if text == "" or text in skipWords:
                        continue
                    allText.append(text)
    finally:
        openFile.close()

countMinSketch = CountMinSketch(kUser, mUser, pUser, cUser, skipWords)

countMinSketch.updateCMSketch(allText)
kTop = countMinSketch.kTopElements(allText)
freq_approx = {x: countMinSketch.frequencyEstimation(x) for x in kTop}
freq_ref = countMinSketch.frequencyRef(allText)

# print result
result = countMinSketch.getResult(freq_approx, freq_ref)
print(result)


resultFile = open('result.txt', 'w')
try:
    resultFile.write('inputPath: ' + inputPath + '\n')
    resultFile.write('k: ' + str(kUser) + '\n')
    resultFile.write('m: ' + str(mUser) + '\n')
    resultFile.write('p: ' + str(pUser) + '\n')
    resultFile.write('c: ' + str(cUser) + '\n')
    resultFile.write(result.to_string())
finally:
    resultFile.close()
