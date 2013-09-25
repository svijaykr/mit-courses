# John Wang
# athenahealth Interview Solution
#
# 9/15/2013

import math
import collections

def word_rank(word):
    if len(word) <= 1:
        return 1

    first_letter = word[0]
    smaller_words = 0
    used_letters = set()

    for i in xrange(1, len(word)):
        current_letter = word[i]
        if first_letter > current_letter and current_letter not in used_letters:
            used_letters.add(current_letter)
            smaller_words += permutations(word[:i] + word[i+1:])

    return smaller_words + word_rank(word[1:])

def permutations(letters):
    return math.factorial(len(letters)) / repetition_factor(letters)

def repetition_factor(letters):
    unique_words = collections.defaultdict(int)
    for letter in letters:
        unique_words[letter] += 1

    factor = 1
    for word, count in unique_words.iteritems():
        factor *= math.factorial(count)

    return factor

if __name__ == '__main__':
    print word_rank('AAAB'), 1
    print word_rank('BAB'), 2
    print word_rank('ABAB'), 2
    print word_rank('BAAA'), 4
    print word_rank('QUESTION'), 24572
    print word_rank('BOOKKEEPER'), 10743
