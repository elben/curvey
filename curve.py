from __future__ import division
import math
import pygame
import sys
from pygame.locals import *



################################################################################
class Lagrange(object):

    def __init__(self, P, t):
        n = len(t)                                                              # get len(t)
        assert len(P) == n                                                      # number of time points must equal number of control points
        x, y = [], []                                                           # initialize x, y
        for p in P: x.append(p[0]); y.append(p[1])                              # split points into x and y
        self.x, self.y = x, y                                                   # set self.x, y
        self._n = xrange(n)                                                     # initialize time/control point iterator
        self.t = t                                                              # set self.t

    def __call__(self, t_):
        x, y, t, _n = self.x, self.y, self.t, self._n                           # cache
        x_, y_ = 0, 0                                                           # initialize x and y return values
        for i in _n:                                                            # iterate over time/control points
            p_i = 1                                                             # initialize lagrange polynomial value
            for j in _n:                                                          # inner iteration over time and control points
                if i != j: p_i *= (t_ - t[j]) / (t[i] - t[j])                       # if i != j: calculate lagrange polynomial
            x_ += x[i] * p_i                                                      # mult ith control point by ith lagrange polynomial (ith control point maps to ith time point)
            y_ += y[i] * p_i                                                      #
        return x_, y_


class Bezier(object):

    def __init__(self, P):
        x, y = [], []                                                           # initialize x, y
        for p in P: x.append(p[0]); y.append(p[1])                              # split points into x and y
        self.x, self.y = x, y                                                   # set self.x, y
        self._n = xrange(len(P))                                                # initialize control point iterator

    def __call__(self, t):
        assert 0 <= t <= 1                                                      # t in [0, 1]
        x, y, _n = self.x, self.y, self._n                                      # cache
        C = self.C                                                              # cache binomial coefficient function
        x_, y_, n = 0, 0, _n[-1]                                                # initialize x, y return values and n
        for i in _n:                                                            # iterate over control points
            b_i = C(i, n) * t**i * (1 - t)**(n - i)                               # calculate bernstein polynomial
            x_ += x[i] * b_i                                                      # mult ith control point by ith bernsteim polynomial (t = 0 maps to first control point, t = 1 maps to nth control point)
            y_ += y[i] * b_i                                                      #
        return x_, y_

    def C(self, i, n):
        factorial = math.factorial                                              # cache
        return factorial(n) / (factorial(i) * factorial(n - i))                 # binomial coefficient == n! / (i!(n - i)!)


class Bspline(object):
#   P == vector of two-dimensional control points
#   t == vector of non-decreasing real numbers
#   k == degree of curve
    def __init__(self, P, t, k = None):
    #   P = (P[0], ... P[n]); n = len(P) - 1
    #   t = (t[0], ... t[m]); m = len(t) - 1
    #   k = m - n - 1
    #   m = n + k + 1
    #   n = m - k - 1
        m, n = len(t) - 1, len(P) - 1                                           # get m, n
        if not k: k = m - n - l                                                 # if not k: k = m - n - 1
        else: assert m == n + k + 1                                             # if k, assert k is valid
        self.k, self.t = k, t                                                   # set k, t
        x, y = [], []                                                           # initialize x, y
        for p in P: x.append(p[0]); y.append(p[1])                              # split p in P into x, y
        self.x, self.y = x, y                                                   # set x, y
        self._deboor()                                                          # evaluate

    def __call__(self, t_):
    #   S(t) = sum(b[i][k](t) * P[i] for i in xrange(0, n))
    #   domain: t in [t[k - 1], t[n + 1]]
        k, t = self.k, self.t                                                   # cache k, t
        m = len(t) - 1                                                          # get m
        n = m - k - 1                                                           # get n
        assert t[k - 1] <= t_ <= t[n + 1]                                       # assert t in [t[k - 1], t[n + 1]]
        x, y, b = self.x, self.y, self.b                                        # cache x, y, b
        x_, y_, _n = 0, 0, xrange(n + 1)                                        # initialize return values, iterator over P
        for i in _n:                                                            # iterate over P
            b_i = b[i][k](t_)                                                     # calculate b[i][k](t)
            x_ += x[i] * b_i                                                      # update x vector
            y_ += y[i] * b_i                                                      # update y vector
        return x_, y_                                                           # return x, y

    def _deboor(self):
    #   de Boor recursive algorithm
    #   S(t) = sum(b[i][k](t) * P[i] for i in xrange(0, n))
    #   b[i][k] = {if k == 0:           t[i] <= t_ < t[i + 1],
    #              else:                a[i][k](t) * b[i][k - 1](t) + (1 - a[i + 1][k](t)) * b[i + 1][k - 1](t)}
    #   a[i][k] = {if t[i] == t[i + k]: 0,
    #              else:                (t_ - t[i]) / (t[i + k] - t[i])}
    #   NOTE: for b[i][k](t), must iterate to t[:-1]; the number of [i, i + 1) spans in t
        k, t = self.k, self.t                                                   # cache k, t
        m = len(t) - 1                                                          # get m
        a, b, _k, _m = [], [], xrange(k + 1), xrange(m)                         # initialize a, b, iterator over k, iterator over t[:-1]
        for i in _m:                                                            # iterate over t[:-1]
            a.append([]); b.append([])                                            # a[i]; b[i]
            for k in _k:                                                          # iterate over k
                a[i].append(None)                                                   # a[i][k]
                if k == 0: b[i].append(lambda t_, i = i: t[i] <= t_ < t[i + 1])     # if k == 0: b[i][k](t) is a step function in [t[i], t[i + 1])
                elif m < i + k: b[i].append(lambda t_: False)                       # if m < i + k: b[i][k](t) undefined
                else:                                                               # else: calculate b[i][k](t)
                    if t[i] == t[i + k]: a[i][k] = lambda t_: False                   # if t[i] == t[i + k]: a[i][k] undefined
                    else:                                                             # else: calculate a[i][k](t)
                        a[i][k] = lambda t_, i = i, k = k: ((t_ - t[i]) /
                                                           (t[i + k] - t[i]))           # a[i][k](t) = (t_ - t[i]) / (t[i + k] - t[i])
                    b[i].append(lambda t_, i = i, k = k:
                                    a[i][k](t_) * b[i][k - 1](t_) +
                                    (1 - a[i + 1][k](t_)) * b[i + 1][k - 1](t_))      # b[i][k](t) = a[i][k](t) * b[i][k - 1](t) + (1 - a[i + 1][k](t)) * b[i + 1][k - 1](t)
        self.b = b                                                              # set b

    def insert(self, t_):
    #   Q[i] = (1 - a[i][k]) * P[i] + a[i][k] * P[i]
    #   domain: t != 0 or 1, t in (t[0], t[m])
        t = self.t                                                              # cache t
        assert t[0] < t_ < t[-1]                                                # assert t_ in (t[0], t[m])
        x, y, k = self.x, self.y, self.k                                        # cache x, y, k
        m = len(t) - 1                                                          # get m
        _m = xrange(m + 1)                                                      # initialize iterator over t
        for i in _m:                                                            # iterate over t
            if t[i] <= t_ < t[i + 1]: break                                       # find the span containing t_, break
        assert not i < k + 1 and not i > m - k + 1                              # assert i not in clamp
        Q_x, Q_y = [], []                                                       # initialize Q
        for j in xrange(i - k + 1, i + 1):                                      # iterate over replaced control points
            a_j = (t_ - t[j]) / (t[j + k] - t[j])                                 # initialize a_j
            Q_x.append((1 - a_j) * x[j - 1] + a_j * x[j])                         # calculate new Q[j]_x
            Q_y.append((1 - a_j) * y[j - 1] + a_j * y[j])                         # calculate new Q[j]_y
        self.t = t[:i + 1] + [t_] + t[i + 1:]                                   # set t
        self.x = x[:i - k + 1] + Q_x + x[i:]                                    # set x
        self.y = y[:i - k + 1] + Q_y + y[i:]                                    # set y
        self._deboor()                                                          # re-evaluate



if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        print 'psyco unavailable'
        pass
    pygame.init()
    SCREEN_SIZE = (800, 600)
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    rect = pygame.rect.Rect((0, 0), SCREEN_SIZE)
    surface = pygame.Surface(SCREEN_SIZE)
    pxarray = pygame.PixelArray(surface)
    P = [(0, 100), (100, 0), (200, 0), (300, 100), (400, 200), (500, 200), (600, 100), (400, 400), (700, 50), (800, 200)]
    n = len(P) - 1                                                          # n = len(P) - 1; (P[0], ... P[n])
    k = 3                                                                   # degree of curve
    m = n + k + 1                                                           # property of b-splines: m = n + k + 1
    _t = 1 / (m - k * 2)                                                    # t between clamped ends will be evenly spaced (not a necessary condition, however)
    # the endpoints of clamped splines have a multiplicity of k + 1 (the endpoint knots are repeated k + 1 times)
    t = k * [0] + [t_ * _t for t_ in xrange(m - (k * 2) + 1)] + [1] * k     # clamp ends and get the t between them (+1 in the xrange to iterate to index m - k * 2)
    S = Bspline(P, t, k)
    S.insert(0.9)                                                           # insert a knot (just to demonstrate the algorithm is working)
    step_len = SCREEN_SIZE[0] * SCREEN_SIZE[1]                              # use small step size to ensure curve is fully drawn (the resolution of the screen guarantees complete draw, but is complete overkill)
    step = 1 / step_len                                                     # create an interval for stepping over t
    for i in xrange(step_len):                                              # iterate 
        t_ = i * step                                                         # get the t_
        try: x, y = S(t_)                                                     # get the vector
        except AssertionError: continue                                       # if vector not defined here (t_ is out of domain): skip
        x, y = int(x), int(y)
        pxarray[x][y] = (255, 0, 0)
    del pxarray
    for p in zip(S.x, S.y): pygame.draw.circle(surface, (0, 255, 0), p, 3, 0)
    SCREEN.blit(surface, (0, 0))
    while 1:
        for event in pygame.event.get():                                      #loop through all events
            if event.type == KEYDOWN:                                           #if keypress:
                if event.key == K_q: sys.exit()
        pygame.display.update()
