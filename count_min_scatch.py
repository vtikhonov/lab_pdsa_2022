import numpy as np

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


to_skip = ["the", "a", "i", "we", "you", "they", "he", "she", "me", "us", "them", "him", "her"]
arr = []

with open("oz.txt", "r") as oz:
    for line in oz:
        for word in line.split():
            if word not in to_skip:
                arr.append(word)


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
print(sketch)
for word in arr:
    hashes = [i.getHashValue(word) for i in hash_functions]
    for i in range(hash_len):
        sketch[i, hashes[i]] += 1

word = arr[33]
print(sketch)
print(word)
hashes = [i.getHashValue(word) for i in hash_functions]
result = []
for i in range(hash_len):
    result.append(sketch[i, hashes[i]])
print(result)

count = 0
for i in arr:
    if i == word:
        count += 1
print(count)

print(len(arr))
