# Curvey

import sys

DEBUG = False

def printar(headline, points):
    for p in points:
        print p

class BSpline(object):
    def __init__(self, points=None, knotvec=None):
        # points isn't in any particular order.
        # A list of (x, y) tuples.
        self.points = points if points else []

        if type(knotvec) == type([]):
            self.knotvec = KnotVector(knotvec)
        elif type(knotvec) == ControlPoint:
            self.knotvec = knotvec.copy()
        else:
            self.knotvec = KnotVector()

    def insert(self, knot):
        old_polars = self.knotvec.control_points()
        self.knotvec.insert(knot)
        new_polars = self.knotvec.control_points()
        new_points = []

        merged_polars = []
        merged_polars.extend(old_polars)
        for polar in new_polars:
            if polar not in merged_polars:
                merged_polars.append(polar)
        merged_polars.sort()

        if DEBUG:
            printar('Old Polars', old_polars)
            printar('New Polars', new_polars)
            printar('Merge Polars', merged_polars)

        for i, polar in enumerate(merged_polars):
            if polar in old_polars:
                # Control point already exists, so we don't need to recalculate
                # its x, y.

                # If this point is not deleted by the insertion, add it.
                if polar in new_polars:
                    new_points.append(self._polar_to_control_point(polar))
                continue

            # New control point. Interpolate between the control points next to
            # it.

            left = self._polar_to_control_point(merged_polars[i-1])
            right = self._polar_to_control_point(merged_polars[i+1])
            middle = ControlPoint(knots=merged_polars[i])
            middle.interpolate(left, right)

            new_points.append(middle)

        new_points.sort()
        self.points = new_points

        if DEBUG:
            printar("Points after insertion:", self.points)

    def _insert_control_point(self, cp):
        # TODO
        pass

    def _polar_to_control_point(self, polar):
        """
        Given a KnotVector representing the polar coordinates of a ControlPoint,
        find the corresponding ControlPoint.
        """
        for cp in self.points:
            if polar == cp.polar():
                return cp

    def render(self, dt=.1):
        """
        Run the de Boor algorithm. Return list of x, y coordinates, ready to be
        rendered.
        """
        # TODO

class ControlPoint(object):
    def __init__(self, point=None, x=None, y=None, knots=None, degree=3):
        self.p = point if point else Point()
        if x:
            self.p.x = x
        if y:
            self.p.y = y
        
        if type(knots) == type([]):
            self._knots = KnotVector(knots)
        elif type(knots) == KnotVector:
            self._knots = knots.copy()
        else:
            self._knots = KnotVector()

    def __str__(self):
        return "(%d, %d) %s" % (self.p.x, self.p.y, self.polar())

    def polar(self):
        return self._knots

    def x(self, x=None):
        if not x:
            return self.p.x
        self.p.x = x

    def y(self, y=None):
        if not y:
            return self.p.y
        self.p.y = y

    def __cmp__(self, other):
        """
        Returns 0 if equal, negative if self < other, and positive if self >
        other.
        """
        return self.polar().__cmp__(other.polar())

    def interpolate(self, left, right, degree=3):
        """
        Given left, right, and this ControlPoints, sets x, y values.

        Returns tuple (a, b, c), which are the differring knots for left,
        right, and this respectively.

        Assumes the KnotVectors of each ControlPoints are legit. If not, throws
        IllegalKnotVectorException.
        """

        try:
            lefti, middlei = KnotVector.difference(left.polar(), self.polar())
            righti, middlei = KnotVector.difference(right.polar(), self.polar())
        except IllegalKnotVectorException as e:
            raise e

        a = left.polar().at(lefti)
        b = right.polar().at(righti)
        c = self.polar().at(middlei)

        self.p.x = float((b-c)*left.x() + (c-a)*right.x())/(b-a)
        self.p.y = float((b-c)*left.y() + (c-a)*right.y())/(b-a)
        return a, b, c


class IllegalKnotVectorException(Exception):
    pass

class KnotVector(object):
    def __init__(self, vec=None, degree=3):
        self.degree = degree
        self.vec = vec if vec else []

    @staticmethod
    def similar(*args):
        """
        Return a set containing the knots that are similar.
        """
        sharedknots = []
        for kv in args:
            sharedknots = sharedknots & set(kv)
        return sharedknots

    @staticmethod
    def difference(a, b, degree=3):
        """
        Assuming there is one differing knot in the polar coordinate a, b,
        return a tuple (ai, bi), which are the indexes to the differring knots
        in a and b, respectively.

        NOTE: ai and bi will be the first index that differs. Thus, [0, 4, 4]
        and [0, 4, 5] will return (1, 2) because the difference is 4 and 5.
        """
        a.sort()
        b.sort()

        acopy = a.copy()
        bcopy = b.copy()

        if a == b:
            return None

        ia = 0
        while ia < len(acopy.vec):
            if acopy.vec[ia] in bcopy.vec:
                ib = bcopy.vec.index(acopy.vec[ia])
                del acopy.vec[ia]
                del bcopy.vec[ib]
            else:
                ia += 1 

        if len(acopy.vec) != 1 or len(bcopy.vec) != 1:
            raise IllegalKnotVectorException(("""More than one differing knot value. acopy: %s,
                    bcopy: %s""" % (str(acopy.vec), str(bcopy.vec))))
        return a.vec.index(acopy.vec[0]), b.vec.index(bcopy.vec[0])

    def __str__(self):
        return "KnotVector: " + str(self.vec)

    def at(self, i):
        return self.vec[i]

    def control_points(self, return_old=False):
        """
        Return a list of KnotVectors that corresponds to the polar notation for
        the control points.
        """
        vectors = []

        if len(self.vec) < 3:
            return vectors

        i = 0
        while i <= (len(self.vec) - 3):
            vectors.append(KnotVector(self.vec[i:i+3]))
            i += 1
        return vectors

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
        return kv

    def __cmp__(self, other):
        """
        Returns 0 if equal, negative if self < other, and positive if self >
        other.

        NOTE: undefined when len(self) != len(other).
        """
        self.vec.sort()
        other_knots = other.sort_copy()
        
        for v1, v2 in zip(self.vec, other_knots.vec):
            if v1 != v2:
                return v1 - v2
        return 0    # equal

    def __eq__(self, other):
        return self.vec == other.vec

    def __ne__(self, other):
        return not (self == other)

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def copy(self):
        p = Point(self.x, self.y)
        return p

    def __cmp__(self, other):
        return self.x == other.x and self.y == other.y
