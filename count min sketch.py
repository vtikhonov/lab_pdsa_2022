#chosen book is Wuthering Heights by Emily Bronte
import numpy as np
import re
limit_size = 1000


class My_Hash:
    def __init__(self, prime_number, odd_number):
        self.prime = prime_number
        self.odd = odd_number

    def getHashValue(self, character):
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
    hash_len = len(hash_functions)

    sketch = np.zeros([hash_len, limit_size])
    print(sketch)
    word_freq_list = []
    for word in full_word_list:
        hashes = [i.getHashValue(word) for i in hash_functions]
        for i in range(hash_len):
            sketch[i, hashes[i]] += 1
        if [min(hashes), word] not in word_freq_list:
            word_freq_list.append([min(hashes), word])
        # print(hashes)
    # print(sketch)
    word_freq_list.sort()

    #for selection multiple top k
    # k = 5 #top k most frequent word
    # top_k_list = word_freq_list[-k:]
    # print(word_freq_list[-k:])
    #
    # top_word_list = []
    # for qty, word in top_k_list:
    #     print(f"the count min sketch qty for word {word} is {qty}")
    #     top_word_list.append(word)
    #
    # real_top_word_list = []
    # for element in top_word_list:
    #     count = 0
    #     for i in full_word_list:
    #         if i == element:
    #             count += 1
    #     real_top_word_list.append([count, element])
    # print(real_top_word_list)
    # for qty, word in real_top_word_list:
    #     print(f"the real qty for word {word} is {qty}")



    # for selection of certain word from text
    selected_word = full_word_list[26] #selecet needed word
    hashes = [i.getHashValue(selected_word) for i in hash_functions]
    result = []
    for i in range(hash_len):
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