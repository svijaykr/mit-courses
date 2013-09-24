import sys

def smallest_integer(integers):
    integers = sorted(list(set(integers)))
    for i in xrange(len(integers)):
        if integers[i] != i+1:
            return i+1
    return len(integers)+1

def smallest_integer_faster(integers):
    integer_bits = [0 for i in xrange(len(integers))]
    for i in integers:
        if i < len(integer_bits):
            integer_bits[i] = 1

    real_bits = integer_bits[1:]
    for i in xrange(len(real_bits)):
        if real_bits[i] == 0:
            return i+1
    return len(real_bits)+2

def test_simple():
    integers = [1,2,3,5,6,7]
    return 4 == smallest_integer_faster(integers)

def test_end():
    integers = [1,2,3,4,5,6,7,8]
    return 9 == smallest_integer_faster(integers)

def test_repeated():
    integers = [1,1,1,2,3,3,4,4,6,6,6,7]
    return 5 == smallest_integer(integers) and 5 == smallest_integer_faster(integers)

def test_null():
    integers = []
    return 1 == smallest_integer(integers)

if __name__ == '__main__':
    print test_simple()
    print test_end()
    print test_repeated()
    print test_null()
