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

max_word1 = ''; max_word2 = ''; max_word3 = ''; max_word4 = ''; max_word5 = ''
max_count1 = 0; max_count2 = 0; max_count3 = 0; max_count4 = 0; max_count5 = 0

skiplist = ["the", "a", "i", "we", "you", "they", "he", "she", "me", "us", "them", "him", "her", "and", "of", "his",
            "to", "in", "was", "were", "has", "had", "have", "that", "this", "those", "with", "it", "as", "for", "at",
            "which", "mr", "mrs", "by", "on", "be", "but"]

for i in range(len(unique)):
    if unique[i] not in skiplist:
        max_count_test = words.count(unique[i])
        if max_count1 < max_count_test:
            max_count1 = max_count_test
            max_word1 = unique[i]

for i in range(len(unique)):
    if unique[i] not in skiplist:
        max_count_test = words.count(unique[i])
        if max_count2 < max_count_test and unique[i] != max_word1:
            max_count2 = max_count_test
            max_word2 = unique[i]

for i in range(len(unique)):
    if unique[i] not in skiplist:
        max_count_test = words.count(unique[i])
        if max_count3 < max_count_test and unique[i] != max_word1 and unique[i] != max_word2:
            max_count3 = max_count_test
            max_word3 = unique[i]

for i in range(len(unique)):
    if unique[i] not in skiplist:
        max_count_test = words.count(unique[i])
        if max_count4 < max_count_test and unique[i] != max_word1 and unique[i] != max_word2 and unique[i] != max_word3:
            max_count4 = max_count_test
            max_word4 = unique[i]

for i in range(len(unique)):
    if unique[i] not in skiplist:
        max_count_test = words.count(unique[i])
        if max_count5 < max_count_test and unique[i] != max_word1 and unique[i] != max_word2 and unique[i] != max_word3 and unique[i] != max_word4:
            max_count5 = max_count_test
            max_word5 = unique[i]

print(max_count1, max_word1)
print(max_count2, max_word2)
print(max_count3, max_word3)
print(max_count4, max_word4)
print(max_count5, max_word5)
# print(words.count('a'))
