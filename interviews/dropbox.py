david.b.stein@dropbox.com
john wang

number_map = {1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five'}

tens_map = {2: 'twenty',
        3: 'thirty',
        4: 'forty',
        5: 'fifty'}

teens_map = {1: 'eleven',
        2: 'twelve',
        3: 'thirteen',
        4: 'fourteen',
        5: 'fifteen'}

exponents_of_thousand = {1: 'thousands',
        2: 'millions',
        3: 'billions',
        4: 'trillions'}

def number_to_word_trillion(integer)
    coefficients = []
    last_coefficient = 0
    for i in xrange(4,-1,-1):
        coefficients.append((integer - last_coefficient * 1000**(i+1)) / 1000**i)
        last_coefficient = coefficients[-1]

def number_to_word(integer):
    hundreds = integer / 100
    tens = (integer - hundreds*100) /10
    ones = (integer - hundreds*100 - tens*10)

    word_list = []
    if hundreds > 0:
        word_list.append(number_map[hundreds])
        word_list.append('hundred')

    if tens > 0:
        if tens != 1:
            word_list.append(tens_map[tens])
        else:
            if ones > 0:
                word_list.append(teens_map[ones])
            else:
                word_list.append('ten')

    if ones > 0 and tens != 1:
        word_list.append(number_map[ones])

    return ' '.join(word_list)

def test_regular_case():
    integer = 342
    return 'three hundred forty two' == number_to_word(integer)

def test_teens_case():
    integer = 13
    return 'thirteen' == number_to_word(integer)

def test_tens_case():
    integer = 110
    return 'one hundred ten' == number_to_word(integer)

if __name__ == '__main__':
    print test_regular_case()
    print test_teens_case()
    print test_tens_case()

