import random

def flip_one_coin():
    if random.random() < 0.5:
        return 0
    else:
        return 1

# flip "num" of coins
def flip_coins(num):
    coin_flips = []
    for x in xrange(num):
        coin_flips.append(flip_one_coin())
    return coin_flips


def find_proportions(number_of_trials):
    proportions = []
    for x in xrange(number_of_trials):
        y = x+1
        coin_flips = flip_coins(y)
        percent_of_heads = float(sum(coin_flips)) / y
        proportions.append(abs(percent_of_heads - 0.5))
    return proportions
    
