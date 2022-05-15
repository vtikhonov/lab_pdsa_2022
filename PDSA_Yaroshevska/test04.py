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

