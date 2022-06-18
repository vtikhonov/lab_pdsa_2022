import numpy as np
import string
import pandas as pd

limit_size = 5000


class HashFunction:
    def __init__(self, prime, odd):
        self.prime = prime
        self.odd = odd

    def getHashValue(self, character):
        hash_val = hash(character)
        if (hash_val < 0):
            hash_val = abs(hash_val)
        return self.calculateHash(hash_val, self.prime, self.odd)

    def calculateHash(self, hash, prime, odd):
        return ((((hash % limit_size) * prime) % limit_size) * odd) % limit_size


to_skip = []
with open("skip_words.txt", "r") as skip:
    for line in skip:
        for word in line.split():
            to_skip.append(word)

# print("To skip: ", to_skip)
arr = []

with open("oz.txt", "r") as oz:
    for line in oz:
        for word in line.split():
            word = word.translate(str.maketrans('', '', string.punctuation))
            word = word.lower()
            word = word.replace('“', '')
            word = word.replace('”', '')
            # print(word)
            if word not in to_skip:
                arr.append(word)


# 7 hash functions
h1 = HashFunction(11, 9)
h2 = HashFunction(17, 15)
h3 = HashFunction(31, 29)
h4 = HashFunction(61, 59)
h5 = HashFunction(17, 3)
h6 = HashFunction(281, 21)
h7 = HashFunction(613, 3333)

hash_functions = [h1, h2, h3, h4, h5, h6, h7]
hash_len = len(hash_functions)

sketch = np.zeros([hash_len, limit_size])
for word in arr:
    hashes = [i.getHashValue(word) for i in hash_functions]
    for i in range(hash_len):
        sketch[i, hashes[i]] += 1

print(f"Number of words: {len(arr)} \n")


df = pd.DataFrame(data=arr)
df = pd.DataFrame(data=df[[0]].value_counts(), columns=["freq_ref"])
df.rename_axis('words',inplace=True)

df["freq_approx"] = np.zeros(df.shape[0])
freq_dict = {}
for i in list(set(arr)):
    hashes = [k.getHashValue(i) for k in hash_functions]
    result = []
    for j in range(hash_len):
        result.append(sketch[j, hashes[j]])

    freq_dict[i] = min(result)

for i in df.index:
    df.loc[i[0], "freq_approx"] = freq_dict[i[0]]

df.sort_values(by=["freq_ref"], inplace=True, ascending=False)
df["error"] = abs(df["freq_ref"] - df["freq_approx"])/df["freq_ref"]*100
print(df.head(10))

# print(df.head(50))

