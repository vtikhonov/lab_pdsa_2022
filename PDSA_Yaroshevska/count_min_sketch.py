import numpy as np

class CountMinSketch(object):

    def __init__(self, m, p, hash_func_family, M=None):
        self.m = m
        self.p = p
        self.hash_func_family = hash_func_family
        if len(hash_func_family) != m:
            raise ValueError("The number of hash functions must match match the depth. (%s, %s)" % (m, len(hash_func_family)))
        if M is None:
            self.M = np.zeros([m, p], dtype=np.int32)
        else:
            self.M = M

    def add(self, x, delta=1):
        for i in range(self.m):
            self.M[i][self.hash_func_family[i](x) % self.p] += delta

    def batch_add(self, lst):
        pass

    def query(self, x):
        return min([self.M[i][self.hash_func_family[i](x) % self.p] for i in range(self.m)])

    def get_matrix(self):
        return self.M

text_file = open('Oliver_Twist_test.txt', 'r', encoding='UTF-8')
text = text_file.read()

#cleaning
text = text.lower()
words = text.split()
words = [word.strip('.,!;()[]_') for word in words]
words = [word.replace("'s", '') for word in words]
words.remove("the")

#finding unique
unique = []
for word in words:
    if word not in unique:
        unique.append(word)

#sort
unique.sort()

max_words = [0] * 5
max_count = [0] * 5

skiptext_file = open('skip_words_new.txt', 'r', encoding='UTF-8')
skiptext = skiptext_file.read()
skiplist = skiptext.split()
# print(skiplist)

for k in range(0, 5):
    for i in range(len(unique)):
        if unique[i] not in skiplist and unique[i] not in max_words:
            max_count_test = words.count(unique[i])
            if max_count_test >= max_count[k]:
                max_count[k] = max_count_test
                max_words[k] = unique[i]

print(max_words)
print(max_count)