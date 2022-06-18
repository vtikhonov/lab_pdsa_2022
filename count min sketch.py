#chosen book is Wuthering Heights by Emily Bronte
import numpy as np
import re
limit_size = 3000
import pandas as pd

class My_Hash:
    def __init__(self, prime_number, odd_number):
        self.prime = prime_number
        self.odd = odd_number

    def getMyHashValue(self, character):
        hash_val = hash(character)
        if (hash_val <0):
            hash_val = abs(hash_val)
        return ((((hash_val % limit_size) * self.prime) % limit_size) * self.odd) % limit_size


if __name__ == '__main__':
    skip_words_file = open('skip_word.txt', 'r')
    skip_words = skip_words_file.read()
    skip_words_list = skip_words.split()
    skip_words_file.close()

    full_file = open('Wuthering Heights by Emily Bronte.txt', 'r', encoding="UTF-8")
    full_text = full_file.read()
    full_text = full_text.lower()
    full_file.close()
    full_word_list = []
    for word in full_text.split():
        pattern = "[':;,.!?“”_]"
        word = re.sub(pattern, "", word)
        if word not in skip_words_list:
            full_word_list.append(word)

    h1 = My_Hash(3, 5)
    h2 = My_Hash(11, 17)
    h3 = My_Hash(17, 31)
    h4 = My_Hash(53, 43)
    h5 = My_Hash(73, 55)
    h6 = My_Hash(83, 37)
    h7 = My_Hash(101, 79)
    h8 = My_Hash(127, 105)
    h9 = My_Hash(139, 93)
    h10 = My_Hash(149, 103)

    hash_functions = [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10]
    hash_length = len(hash_functions)

    sketch = np.zeros([hash_length, limit_size])
    print(sketch)
    word_freq_list = []
    for word in full_word_list:
        hashes = [i.getMyHashValue(word) for i in hash_functions]
        for i in range(hash_length):
            sketch[i, hashes[i]] += 1

    # for selection of one certain word from text
    selected_word = "book" #selecet needed word choose from full_word_list- full_word_list[10] for example
    hashes = [i.getMyHashValue(selected_word) for i in hash_functions]
    result = []
    for i in range(hash_length):
        result.append(sketch[i, hashes[i]])
    count = 0
    for i in full_word_list:
        if i == selected_word:
            count += 1
    print("Min sketch final array\n", result)
    print("All words qty = ", len(full_word_list))

    print(f"REAL qty of word *{selected_word}* = {count}")
    print(f"Qty according to min sketch of word *{selected_word}* = {min(result)}")

    print(f"REAL frequency of word *{selected_word}* = {(count / len(full_word_list)) *100} %")

    print(f"Frequency according to min sketch of word *{selected_word}* = {(min(result) / len(full_word_list)) *100} %")
    print(("Enter k number"))
    k = int(input())
    df = pd.DataFrame(data=full_word_list)
    df = pd.DataFrame(data=df[[0]].value_counts(), columns=["freq_real"])
    ktop_freg = {}
    for i in list(set(full_word_list)):
        hash_results = [k.getMyHashValue(i) for k in hash_functions]
        result = []
        for j in range(hash_length):
            result.append(sketch[j, hash_results[j]])
        ktop_freg[i] = min(result)
    for word in set(full_word_list):
        df.loc[word, "freq_count_min"] = ktop_freg[word]

    df.sort_values(by=["freq_real"], ascending=False)
    df["error"] = round(abs(df["freq_real"] - df["freq_count_min"])/df["freq_real"]*100, 2)
    print(df.head(k))
