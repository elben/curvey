# Curvey

class BSpline(object):
    def __init__(self, points=None, knotvec=None):
        # points isn't in any particular order.
        # A list of (x, y) tuples.
        self.points = points if points else []
        self.old_points = points if points else []

        if type(knotvec) == type([]):
            self.knotvec = KnotVector(knotvec)
        elif type(knotvec) == ControlPoint:
            self.knotvec = knotvec.copy()
        else:
            self.knotvec = KnotVector()

    def insert(self, knot):
        self.knotvec.insert(knot)
        old_vec = self.knotvec.old_vec
        self.old_points = self.old_points # TODO

        # TODO below is wrong. we need to go get the 
        polar_vecs = self.knotvec.control_points()
        for i, polar in enumerate(polar_vecs):
            if polar in self.points: # TODO fix this wrongness
                # Control point already exists, so we don't need to recalculate
                # its x, y.
                continue

            # New control point. Interpolate between the control points next to
            # it.

            # TODO we might be at the ends, so i-1 and i+1 might crash. If we're
            # at the end, then... not sure.

            left = ControlPoint(knot=control_points[i-1])
            right = ControlPoint(knot=control_points[i+1])
            middle = ControlPoint(knot=control_points[i])
            ControlPoint.interpolate(left, right, middle)

            self.points.append(middle)            

    def _insert_control_point(self, cp):
        pass


    def render(self, dt=.1):
        """
        Run the de Boor algorithm. Return list of x, y coordinates, ready to be
        rendered.
        """

class ControlPoint(object):
    def __init__(self, point=None, x=None, y=None, knots=None):
        self.p = point if point else Point()
        if x:
            self.p.x = x
        if y:
            self.p.y = y
        
        if type(knots) == type([]):
            self.knots = KnotVector(knots)
        elif type(knots) == ControlPoint:
            self.knots = knots.copy()
        else:
            self.knots = KnotVector()

    def x(self):
        return self.p.x

    def y(self):
        return self.p.y

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

    @staticmethod
    def interpolate(left, right, middle, degree=3):
        """
        Given left, right, and middle ControlPoints, sets middle's x, y
        values.

        Returns tuple (a, b, c), which are the differring knots for left,
        right, and middle respectively.

        Assumes the KnotVectors of each ControlPoints are legit.
        """

        # TODO this is going to break if there is more than one differring knots
        # and stuff. Stop and unit test this stuff!!!
        left.knots.sort()
        middle.knots.sort()
        right.knots.sort()
        for i in range(degree):
            a = left.knots.at(i)
            b = right.knots.at(i)
            c = middle.knots.at(i)
            if a == b == c:
                continue

            # The knots differ, so interpolate.
            middle.x = float((b-c)*left.x() + (c-a)*right.x())/(b-a)
            middle.y = float((b-c)*left.y() + (c-a)*right.y())/(b-a)
            return a, b, c

class KnotVector(object):
    def __init__(self, vec=None, degree=3):
        self.degree = degree
        self.vec = vec if vec else []

        # We also save the old vector for insertions.
        self.old_vec = self.vec[:]

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

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def copy(self):
        p = Point(self.x, self.y)
        return p

    def __cmp__(self, other):
        return self.x == other.x and self.y == other.y
