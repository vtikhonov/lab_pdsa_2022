import numpy as np
import codecs
import pandas as pd
import argparse
import hashlib

delta = 0.02
epsilon = 0.005


def create_parser():
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation')
    parser.add_argument('--input', type=str, help='Path to file or folder with a textual file', required=False,
                        default='the_souls_of_black_folk.txt')
    parser.add_argument('-k', type=int, help='Number of top frequent element that we are looking for', required=False,
                        default=10)
    parser.add_argument('-m', type=int, help='Count-min sketch buffer size', required=False,
                        default=int(2.7182 / epsilon))
    parser.add_argument('-p', type=int, help='number of independent hash functions', required=False,
                        default=int(np.log(1 / delta)))
    parser.add_argument('-c', type=int, default=32, help='number of bits per counter, default is 12', required=False,
                        choices=[8, 16, 32])
    parser.add_argument('--hash', type=str, required=False,
                        choices=["sha1", "sha224", "sha256", "sha384", "sha512", "md5"])
    return parser


def split(txt, seps):
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]


def create_cm_sketch(c):
    cm_sketch = None
    if c == 8:
        cm_sketch = np.zeros((p, m), dtype='uint8')
    elif c == 16:
        cm_sketch = np.zeros((p, m), dtype='uint16')
    elif c == 32:
        cm_sketch = np.zeros((p, m), dtype='uint32')
    return cm_sketch


def update_cm_sketch(data, cm_sketch):
    for w in data:
        for j in range(p):
            hash_func = get_hash_func(hash_name)
            i = int(hash_func((w + str(j)).encode('utf-8')).hexdigest(), 16) % m
            cm_sketch[j, i] += 1


def cm_frequency_estimation(w, cm_sketch):
    f = []
    for j in range(p):
        hash_func = get_hash_func(hash_name)
        i = int(hash_func((w + str(j)).encode('utf-8')).hexdigest(), 16) % m
        f.append(cm_sketch[j, i])
    return min(f)


def count_exact_word_frequency(data):
    freq = {}
    for w in data:
        if w not in freq.keys():
            freq[w] = 1
        else:
            freq[w] += 1
    sorted_freq = sorted(freq.items(), key=lambda item: int(item[1]), reverse=True)
    return sorted_freq


def get_top_freq_elements(data, cm_sketch):
    X = []
    for w in data:
        if w in X:
            pass
        elif len(X) < k:
            X.append(w)
        else:
            f_w = cm_frequency_estimation(w, cm_sketch)
            X_f = {x: cm_frequency_estimation(x, cm_sketch) for x in X}
            x_min = min(X_f, key=X_f.get)
            f_x_min = X_f[x_min]
            if f_w > f_x_min:
                X.append(w)
                X.remove(x_min)
    return X


def save_result(cm_sketch_freq, exact_freq):
    cm_sketch_freq = dict(sorted(cm_sketch_freq.items(), key=lambda item: int(item[1]), reverse=True))
    df = pd.DataFrame({'word': list(cm_sketch_freq.keys()), 'freq_approx': list(cm_sketch_freq.values())})
    exact_freq = dict(exact_freq)
    freq_ref = []
    for w in cm_sketch_freq.keys():
        freq_ref.append(int(exact_freq[w]))
    df.insert(1, 'freq_ref', freq_ref, True)
    error = []
    for ref, approx in zip(freq_ref, cm_sketch_freq.values()):
        error.append(100 * abs(approx - ref) / ref)
    df.insert(3, 'error', error, True)
    df.to_csv('result.csv', index=False)
    return df


def get_hash_func(hash_name):
    if hash_name is None:
        return hash
    elif hash_name == 'sha1':
        return hashlib.sha1
    elif hash_name == 'sha224':
        return hashlib.sha224
    elif hash_name == 'sha256':
        return hashlib.sha256
    elif hash_name == 'sha384':
        return hashlib.sha384
    elif hash_name == 'sha512':
        return hashlib.sha512
    elif hash_name == 'md5':
        return hashlib.md5


# parse arguments
parser = create_parser().parse_args()
input = parser.input
k = parser.k
m = parser.m
p = parser.p
c = parser.c
hash_name = parser.hash
print('input: ', input)
print('k: ', k)
print('m: ', m)
print('p: ', p)
print('c: ', c)
print('hash: ', hash_name)

# separators list
separators = [' ', ',', '.', ':', ';', '!', '?', '—', '”', '“', '\n']

# list of words to skip
words_skip_f = open('skip_words.txt', 'r')
words_skip = words_skip_f.read()
words_skip = words_skip.split('\n')
words_skip_f.close()

# list of all words in text
f = codecs.open(input, "r", "utf_8_sig")
text = f.read()
words = split(text, separators)
words = [w.lower() for w in words if w.lower() not in words_skip]
f.close()

# frequency by count min sketch
cm_sketch = create_cm_sketch(c)
update_cm_sketch(words, cm_sketch)
X = get_top_freq_elements(words, cm_sketch)
freq_cm_sketch = {x: cm_frequency_estimation(x, cm_sketch) for x in X}

# exact frequency
freq_exact = count_exact_word_frequency(words)

# save and print result
result = save_result(freq_cm_sketch, freq_exact)
print(result)

