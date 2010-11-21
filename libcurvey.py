# Curvey

import sys
import math
from util import *

DEBUG = False

class BSpline(object):
    def __init__(self, points=None, knotvec=None, degree=None, dt=None):
        # A list of Points. Listed in order of user insertion.
        # So the curve is rendered based on the order of points.
        self.user_points = points if points else []
        self._internal_points = points if points else []
        self.degree = degree
        self.dt = dt if dt else 0.2

        if type(knotvec) == type([]):
            self._internal_knotvec = KnotVector(knotvec)
            self.user_knotvec = KnotVector(knotvec)
        elif type(knotvec) == ControlPoint:
            self._internal_knotvec = knotvec.copy()
            self.user_knotvec = knotvec.copy()
        else:
            self._internal_knotvec = KnotVector()
            self.user_knotvec = KnotVector()

    def render(self, dt=None):
        """
        Returns a tuple containing two items:
            The list of control points (as a tuple).
            The list of control points in polar coordinates.
            The list of points to be connected to represent the curve.

        Throws InvalidBSplineException is the spline is not in a valid state for
        rendering. Possible invalid states:
            
            Number of control points not matching the number of knots in the
            knot vector. 
        """
        dt = dt if dt else self.dt
        control_points = []
        control_point_polars = []
        points = []

        for p in self.user_points:
            x, y = p.x(), p.y()
            control_point_polars.append(p.polar().knots())
            control_points.append((x,y))

        for p in self._internal_points:
            x, y = p.x(), p.y()
            points.append((x,y))

        return control_points, control_point_polars, points

    def insert_control_point(self, cp):
        """
        Inserts ControlPoint cp into the spline. This might put the spline into
        an invalid state.

        Thus, the user may have to modify the knot vector before the spline is
        render()-able.
        """
        self.user_points.append(cp)
        self._de_boor()
    
    def remove_control_point(self, cp):
        """
        Removes ControlPoint cp from the spline. This might put the spline into
        an invalid state.
        """
        self.user_points.remove(cp)
        self._de_boor()

    def replace_control_point(self, cp, cpnew):
        """
        Replaces ControlPoint cp with cpnew.
        """
        i = self.user_points.index(cp)
        del self.user_points[i]
        self.user_points.insert(i, cpnew)
        self._de_boor()

    def replace_control_points(self, control_points):
        self.user_points = control_points
        self._de_boor()

    def replace_knot_vector(self, knotvec):
        """
        Replaces the spline's current knot vector with knotvec.
        """

        if type(knotvec) != KnotVector:
            knotvec = KnotVector(knotvec)

        self.user_knotvec = knotvec
        self._de_boor()

    def is_valid(self):
        """
        Returns true if the spline has enough control points and knot vectors
        for the given degree.
        """
        return (len(self.user_points) > self.degree and
                len(self.user_knotvec) == len(self.user_points)+self.degree-1)

    def _de_boor(self, dt=None):
        """
        Runs the de Boor algorithm on the spline to calculate the points to be
        rendered on the screen.

        Implementation details: we insert degree knots every dt in paramater
        space.
        """
        
        # TODO: for now, we implement this the ghetto way. Each time this method
        # is called, we clear everything we've ever had. We then start from
        # scratch and compute every point.
        # This is, of course, a hack and should be optimized.
        
        if not self.is_valid():
            return

        self._internal_points = self.user_points[:]  # TODO copy ControlPoints?
        self._internal_knotvec = self.user_knotvec.copy()
        
        # Tell the ControlPoints their polar coords.
        for i, cp in enumerate(self._internal_points):
            cp.polar(KnotVector(self._internal_knotvec[i:i+self.degree]))

        dt = dt if dt else self.dt
        t = self.user_knotvec.at(self.degree-1)
        t_end = self.user_knotvec.at(-self.degree)

        if DEBUG:
            printar("internal points", self._internal_points)
            printar("internal knotvec", self._internal_knotvec)
            print "t start " + str(t)
            print "t end " + str(t_end)

        drawing_points = []
        while epsilon_less_equal_than(t, t_end):
            needed_knots = self.degree - self._count_knots(t) 
            for i in range(needed_knots):
                self._insert_knot(t)
                if DEBUG:
                    printar("internal knots now", self._internal_knotvec)
            drawing_points.append(self._polar_to_control_point(KnotVector([t]*self.degree)))
            t += dt
        printar("Drawing Points", drawing_points)
        self._internal_points = drawing_points


    def _insert_knot(self, knot):
        """
        Inserts a knot into the knot vector. This will add and remove control
        points as defined by the knot insertion algorithm.
        """

        old_polars = self._internal_knotvec.polar_points(self.degree)
        self._internal_knotvec.insert(knot)
        new_polars = self._internal_knotvec.polar_points(self.degree)
        new_control_points = []

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

                # Keep point if not to be deleted by the insertion.
                if polar in new_polars:
                    new_control_points.append(self._polar_to_control_point(polar))
                continue

            # New control point. Interpolate between the control points next to
            # it.

            if DEBUG:
                printar("Looking at left", merged_polars[i-1])
                printar("Looking at middle", merged_polars[i])
                printar("Looking at right", merged_polars[i+1])
            left = self._polar_to_control_point(merged_polars[i-1])
            right = self._polar_to_control_point(merged_polars[i+1])
            middle = ControlPoint(knots=merged_polars[i])
            try:
                middle.interpolate(left, right)
            except IllegalKnotVectorException as e:
                # This is sometimes expected. For example, it could be that
                # there is nothing at this point in the b-spline.
                # TODO: there must be a better way to check whether or not a
                # point exists on the spline for a given t.
                # Example: the end control points might not match. If they don't
                # match, then we won't have anything at t=0, for example.
                pass

            new_control_points.append(middle)

        self._internal_points = new_control_points

        if DEBUG:
            printar("Points after insertion:", self._internal_points)

    def _polar_to_control_point(self, polar):
        """
        Given a KnotVector representing the polar coordinates of a ControlPoint,
        find the corresponding ControlPoint.
        """
        for cp in self._internal_points:
            if polar == cp.polar():
                return cp
        raise Exception("ControlPoint not found for %s." % (polar,))
        
    def _count_knots(self, knot):
        """
        Returns the number of times knot is found in the internal knot vector.
        """
        count = 0
        for k in self._internal_knotvec:
            if k == knot:
                count += 1
        return count

class ControlPoint(object):
    def __init__(self, point=None, x=None, y=None, knots=None):
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

    def polar(self, knots=None):
        if knots:
            self._knots = knots
        return self._knots

    def x(self, x=None):
        if not x:
            return self.p.x
        self.p.x = x

    def y(self, y=None):
        if not y:
            return self.p.y
        self.p.y = y

    def interpolate(self, left, right):
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

    def copy(self):
        cp = ControlPoint()
        cp.p = self.p.copy()
        cp._knots = self._knots.copy()
        return cp

    def __cmp__(self, other):
        return self.polar().__cmp__(other.polar())

    def __str__(self):
        return "(%.2f, %.2f) %s" % (self.p.x, self.p.y, self.polar())


class IllegalKnotVectorException(Exception):
    pass

class KnotVector(object):
    def __init__(self, vec=None):
        self.vec = vec if vec else []

    def __iter__(self):
        return self.vec.__iter__()

    def __getitem__(self, key):
        # key could be integer or slice object
        return self.vec[key]

    def degree(self):
        return len(self.vec)

    def knots(self):
        return tuple(self.vec)

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
    def difference(a, b):
        """
        Assuming there is one differing knot in the polar coordinate a, b,
        return a tuple (ai, bi), which are the indexes to the differring knots
        in a and b, respectively.

        NOTE: ai and bi will be the first index that differs. Thus, [0, 4, 4]
        and [0, 4, 5] will return (1, 2) because the difference is 4 and 5.
        """

        if a.degree() != b.degree():
            raise IllegalKnotVectorException("Degrees of knot vectors differ.")

        a.sort()
        b.sort()

        acopy = a.copy()
        bcopy = b.copy()

        if a == b:
            return None

        ia = 0
        while ia < len(acopy.vec):
            aknot = acopy.vec[ia]
            for ib, bknot in enumerate(bcopy.vec):
                if epsilon_equals(aknot, bknot):
                    del acopy.vec[ia]
                    del bcopy.vec[ib]
                    break
            else:
                # Increment ia only if we did NOT delete an item from acopy. If item
                # was deleted, then we need to recheck index ia.
                ia += 1 


        if len(acopy.vec) != 1 or len(bcopy.vec) != 1:
            raise IllegalKnotVectorException(("""More than one differing knot value. acopy: %s,
                    bcopy: %s""" % (str(acopy.vec), str(bcopy.vec))))
        return a.vec.index(acopy.vec[0]), b.vec.index(bcopy.vec[0])

    def __str__(self):
        l = []
        for knot in self.vec:
            l.append('%.2f' % knot)
        s = '[%s]' % (', '.join(l))
        return "KnotVector: %s" % s

    def at(self, i):
        return self.vec[i]

    def polar_points(self, degree=3):
        """
        Return a list of KnotVectors that corresponds to the polar notation for
        the control points.
        """
        polars = []

        if len(self.vec) < degree:
            return polars

        i = 0
        while i <= (len(self.vec) - degree):
            polars.append(KnotVector(self.vec[i:i+degree]))
            i += 1
        return polars

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
        """
        Inserts knot into the knot vector at the proper place.
        """

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
            if not epsilon_equals(v1, v2):
                return -1 if epsilon_less_than(v1, v2) else 1
        return 0    # equal

    def __eq__(self, other):
        if len(self.vec) != len(other.vec):
            return False
        for i, j in zip(self.vec, other.vec):
            if not epsilon_equals(i, j):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __len__(self):
        return len(self.vec)

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def copy(self):
        p = Point(self.x, self.y)
        return p

    def __eq__(self, other):
        return epsilon_equals(self.x, other.x) and epsilon_equals(self.y, other.y)

    def __cmp__(self, other):
        """
        Sort by distance to origin, (0, 0).
        """
        d_self = math.sqrt(self.x*self.x + self.y*self.y)
        d_other = math.sqrt(other.x*other.x + other.y*other.y)
        return d_self - d_other
