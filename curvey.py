# Curvey

class ControlPoint(object):
    def __init__(self, x=0, y=0, knots=None):
        self.x = x
        self.y = y
        
        if type(knots) == type([]):
            self.knots = KnotVector(knots)
        else:
            self.knots = knots if knots else KnotVector()

    def __cmp__(self, other):
        """
        Returns 0 if equal, negative if self < other, and positive if self >
        other.
        """
        self.knots.sort()
        other_knots = other.knots.sort_copy()
        
        for v1, v2 in zip(self.knots.vec, other_knots.vec):
            if v1 != v2:
                return v1 - v2
        return 0    # equal

class KnotVector(object):
    def __init__(self, vec=None, degree=3):
        self.degree = degree
        self.vec = vec if vec else []

        # We also save the old vector for insertions.
        self.old_vec = self.vec[:]

    def is_valid(self):
        # Returns true if this is valid knot vector.
        # That is, a non-negative, non-decreasing list of numbers.
        last = -1
        for v in self.vec:
            if v < last:
                return False
            last = v
        return True

    def insert(self, knot):
        # Inserts knot into the knot vector at the proper place.

        self.old_vec = self.vec[:]
        for i, v in enumerate(self.vec):
            if v >= knot:
                self.vec.insert(i, knot)
                return

        # All knots smaller, new knot goes to end.
        self.vec.append(knot)

    def sort(self):
        self.vec.sort()

    def sort_copy(self):
        kv = self.copy()
        kv.vec.sort()
        return kv

    def copy(self):
        kv = KnotVector()
        kv.degree = self.degree
        kv.vec = self.vec[:]
        kv.old_vec = self.old_vec[:]
        return kv

    def __eq__(self, other):
        return self.vec == other.vec
