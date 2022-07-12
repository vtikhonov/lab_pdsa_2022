# -*- coding: utf-8 -*-
from typing import Dict
import hashlib as hl
import pandas as pd
import numpy as np
import argparse
import re


delta = 0.02
epsilon = 0.005
hashFuncList = ['sha1', 'sha224', 'sha256', 'sha384', 'sha512','md5']



def createParser():
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation')
    parser.add_argument('--input',
                        type=str,
                        help='Path to file or folder with a textual file',
                        required=False,
                        default='Frankenstein; Or, The Modern Prometheus by Mary Wollstonecraft Shelley.txt')
    parser.add_argument('-k',
                        type=int,
                        help='Number of top frequent element that we are looking for.',
                        required=False,
                        default=10)
    parser.add_argument('-m',
                        type=int,
                        help='Count-min sketch buffer size',
                        required=False,
                        default=int(np.e / epsilon))
    parser.add_argument('-p',
                        type=int,
                        help='Number of independent hash functions',
                        required=False,
                        default=int(np.log(1 / delta)))


    parser.add_argument('--hash',
                        type=str,
                        required=False,
                        default='md5')
    return parser


class CMSketch:

    def __init__(self, k, m, p, hash, skipWords=None):
        self.k = k
        self.m = m
        self.p = p
        self.hashFunc = hl.new(hash)
        self.cMSketch = np.zeros((p, m))
        self.skipWords = skipWords
        self.wordsDict: Dict[str, int] = {}

    def frequencyEstimation(self, x):
        f = []
        for j in range(self.p):
            hashF = self.hashFunc
            hashF.update((x + str(j)).encode('utf-8'))
            i = int(hashF.hexdigest(), 16) % self.m
            f.append(self.cMSketch[j, i])
        return min(f)

    def exactWordsFrequency(self, data):
        for x in data:
            for j in range(self.p):
                hashF = self.hashFunc
                hashF.update((x + str(j)).encode('utf-8'))
                i = int(hashF.hexdigest(), 16) % self.m
                self.cMSketch[j, i] += 1



    def topFreqElements(self, data):
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
                    X.append(x)
                    X.remove(x_min)

        return X

    @staticmethod
    def frequencyRef(data):
        freq = {}
        for x in data:
            if x not in freq.keys():
                freq[x] = 1
            else:
                freq[x] += 1
        sorted_freq = sorted(freq.items(), key=lambda item: int(item[1]), reverse=True)
        return sorted_freq

    @staticmethod
    def getResult(freqApprox, freqRef):
        freqApproxResult = dict(sorted(freqApprox.items(), key=lambda item: int(item[1]), reverse=True))
        freqRefResult = []
        for x in freqApproxResult.keys():
            freqRefResult.append(int(dict(freqRef)[x]))

        error = []
        for approx, ref in zip(freqApproxResult.values(), freqRefResult):
            error.append(100 * abs(approx - ref) / ref)

        df = pd.DataFrame({'word': list(freqApproxResult.keys()), 'freqApprox': list(freqApproxResult.values())})
        df.insert(1, 'freqRef', freqRefResult, True)
        df.insert(3, 'error', error, True)
        return df


userParser = createParser().parse_args()
inputPath = userParser.input
kUser = userParser.k
mUser = userParser.m
pUser = userParser.p
hashUser = userParser.hash
if hashUser not in hashFuncList:
    print('No such Hash Function')
    exit()
print(inputPath)
print('k:', kUser)
print('m: ', mUser)
print('p: ', pUser)
print('hash: ', hashUser)

# list of separators
separators = re.compile(r'[(\s),.:;!?\n\t\'\\[\]"”“]')

# list of words to skip
skipWordsFunc = open("skip_words.txt", "r")
skipWords = skipWordsFunc.read()
skipWords = skipWords.split('\n')
skipWordsFunc.close()

# list of words to skip
allWords = []
with open(inputPath, "r", encoding="utf-8-sig") as openFile:

        for line in openFile.readlines():
            if line not in skipWords:
                for word in line.split():
                    text = re.sub(separators, "", word.lower())
                    if text == "" or text in skipWords:
                        continue
                    allWords.append(text)


cmSketch = CMSketch(kUser, mUser, pUser, hashUser, skipWords)

# frequency by count min sketch
cmSketch.exactWordsFrequency(allWords)
kTop = cmSketch.topFreqElements(allWords)
freq_approx = {x: cmSketch.frequencyEstimation(x) for x in kTop}

# exact frequency
freq_ref = cmSketch.frequencyRef(allWords)

# print result
result = cmSketch.getResult(freq_approx, freq_ref)
print(result)
open('result.txt', 'w').write(result.to_string())
