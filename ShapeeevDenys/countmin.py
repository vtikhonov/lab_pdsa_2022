import numpy as np
import codecs
import pandas as pd
import argparse

delta = 0.02
epsilon = 0.005


def create_parser():
    parser = argparse.ArgumentParser(description='K-Top frequency with Count-Min Sketch problem implementation')
    parser.add_argument('--input', type=str, help='Path to file  with a textual file', required=False,
                        default='OliverTwistbyCharlesDickens.txt')
    parser.add_argument('-k', type=int, help='Number of top frequent element that we are looking for', required=False,
                        default=12)
    parser.add_argument('-m', type=int, help='Count-min sketch buffer size', required=False,
                        default=int(3.0 / epsilon))
    parser.add_argument('-p', type=int, help='number of independent hash functions', required=False,
                        default=int(np.log(1 / delta)))
    return parser


def split(txt, seps):
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]


def update_cm_sketch(data, cm_sketch):
    for w in data:
        for j in range(p):
            i = hash(w + str(j)) % m
            cm_sketch[j, i] += 1


def cm_frequency_estimation(data, cm_sketch):
    f_dict = {}
    for w_n, w in enumerate(data):
        f = []
        for j in range(p):
            i = hash(w + str(j)) % m
            f.append(cm_sketch[j, i])
        f_dict[w] = min(f)
    sorted_freq = sorted(f_dict.items(), key=lambda item: int(item[1]), reverse=True)
    return sorted_freq


def count_exact_word_frequency(data):
    freq = {}
    for w in data:
        if w not in freq.keys():
            freq[w] = 1
        else:
            freq[w] += 1
    sorted_freq = sorted(freq.items(), key=lambda item: int(item[1]), reverse=True)
    return sorted_freq


def save_result(cm_sketch_freq, exact_freq):
    result = dict(exact_freq[:k])
    df = pd.DataFrame({'word': list(result.keys()), 'freq_approx': list(result.values())})
    cm_sketch_freq = dict(cm_sketch_freq)
    freq_approx = []
    for w in result.keys():
        freq_approx.append(int(cm_sketch_freq[w]))
    df.insert(2, 'freq_approx', freq_approx, True)
    error = []
    freq_ref = result.values()
    for ref, approx in zip(freq_ref, freq_approx):
        error.append(100 * abs(approx - ref) / ref)
    df.insert(3, 'error', error, True)
    df.to_csv('result.csv', index=False)
    return df


# parse arguments
parser = create_parser().parse_args()
input = parser.input
k = parser.k
m = parser.m
p = parser.p
print('input: ', input)
print('k:', k)
print('m: ', m)
print('p: ', p)

# separators list
separators = [' ', ',', '.', ':', ';', '!', '?', '—', '”', '“', '\n']

# list of words to skip
words_skip_f = open('OliverTwistbyCharlesDickens.txt', 'r')
words_skip = words_skip_f.read()
words_skip = words_skip.split('\n')

# list of all words in text
f = codecs.open(input, "r", "utf_8_sig")
text = f.read()
words = split(text, separators)
words = [w.lower() for w in words if w.lower() not in words_skip]

# frequency by count min sketch
cm_sketch = np.zeros((p,m))
update_cm_sketch(words, cm_sketch)
freq_cm_sketch = cm_frequency_estimation(words, cm_sketch)

# exact frequency
freq_exact = count_exact_word_frequency(words)

# save and print result
result = save_result(freq_cm_sketch, freq_exact)
print(result)

f.close()
