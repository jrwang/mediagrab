

def sum_with_sub(int_l):
    '''Sum a list of integers. Replace empty data points with the mean of the items'''
    ints = filter(lambda x: x is not None, int_l)
    subs = filter(lambda x: x is None, int_l)
    avg = float(sum(ints))/len(ints) if ints != [] else 0
    #print ints, subs, avg
    return sum(ints) + avg*len(subs)

def counter_top(counter, n):
    '''Returns top n results from a Counter object, formatting nicely'''
    ret = ''
    for key, count in counter.most_common(n):
        ret += '{} ({}), '.format(key, count)
    return ret[:-2] # to remove trailing comma
