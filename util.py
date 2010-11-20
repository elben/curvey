import sys

def epsilon_equals(f1, f2, epsilon=0.0001):
    return abs(f1-f2) < epsilon

def epsilon_less_than(f1, f2, epsilon=0.0001):
    return f1 < (f2-epsilon)

def printar(headline, points):
    print
    print >> sys.stderr, headline
    for p in points:
        print >> sys.stderr, p

