from libcurvey import *
import unittest

def float_equals(f1, f2, epsilon=.0001):
    return abs(f1-f2) < epsilon

class TestBSpline(unittest.TestCase):
    def setUp(self):
        self.cp1 = ControlPoint(Point(1, 3), knots=[0,0,0])
        self.cp2 = ControlPoint(Point(2, 4), knots=[0,0,1])
        self.cp3 = ControlPoint(Point(6, 5), knots=[0,1,3])
        self.cp4 = ControlPoint(Point(5, 1), knots=[1,3,4])
        self.cp5 = ControlPoint(Point(2, 1), knots=[3,4,4])
        self.cp6 = ControlPoint(Point(0, 2), knots=[4,4,4])
        self.bs1 = BSpline(points=[self.cp1, self.cp2, self.cp3, self.cp4,
            self.cp5, self.cp6], knotvec=[0,0,0,1,3,4,4,4])

    def test_de_boor(self):
        self.bs1._de_boor()
        points = self.bs1._internal_points
        knotvec = self.bs1._internal_knotvec
        self.assertEqual(knotvec, KnotVector([0,0,0,1,2,2,2,3,4,4,4]))

        self.assertTrue(float_equals(self.bs1._internal_points[3].x(), 47.0/9))
        self.assertTrue(float_equals(self.bs1._internal_points[3].y(), 32.0/9))
        self.assertTrue(float_equals(self.bs1._internal_points[4].x(), 46.0/9))
        self.assertTrue(float_equals(self.bs1._internal_points[4].y(), 53.0/18))
        self.assertTrue(float_equals(self.bs1._internal_points[5].x(), 5))
        self.assertTrue(float_equals(self.bs1._internal_points[5].y(), 7.0/3))
        self.assertTrue(float_equals(self.bs1._internal_points[6].x(), 4))
        self.assertTrue(float_equals(self.bs1._internal_points[6].y(), 1))

    def test_is_valid(self):
        self.assertTrue(self.bs1.is_valid())

        bs = BSpline(degree=4)
        self.assertFalse(bs.is_valid())
        bs.insert_control_point(ControlPoint(0, 0))
        self.assertFalse(bs.is_valid())
        bs.insert_control_point(ControlPoint(Point(1, 1)))
        bs.insert_control_point(ControlPoint(Point(0, 2)))
        bs.insert_control_point(ControlPoint(Point(1, 3)))
        bs.replace_knot_vector(range(7))
        self.assertTrue(bs.is_valid())

    def test_polar_to_control_point(self):
        self.assertEqual(self.bs1._polar_to_control_point(KnotVector([0,0,0])),
            self.cp1)
        self.assertEqual(self.bs1._polar_to_control_point(KnotVector([0,1,3])),
            self.cp3)
        self.assertEqual(self.bs1._polar_to_control_point(KnotVector([4,4,4])),
            self.cp6)
        self.assertRaises(Exception,
                self.bs1._polar_to_control_point, KnotVector([100,4,4]))

    def test_insert_knot(self):
        # This follows the example on Figure 12 and 13 of
        # "An Introduction to B-Spline Curves". This tests essentially the de
        # Boor algorithm. We insert knot=2 twice to get P(2,2,2).

        self.bs1._insert_knot(knot=2)
        new_knotvec = KnotVector([0,0,0,1,2,3,4,4,4])
        self.assertEqual(self.bs1._internal_knotvec, new_knotvec)
        # assert new points added to right place and old points removed
        self.assertEqual(self.bs1._internal_points[2].polar(), KnotVector([0,1,2]))
        self.assertEqual(self.bs1._internal_points[3].polar(), KnotVector([1,2,3]))
        self.assertEqual(self.bs1._internal_points[4].polar(), KnotVector([2,3,4]))
        self.assertEqual(self.bs1._internal_points[5].polar(), KnotVector([3,4,4]))
        # assert new points have the right x, y.
        self.assertEqual(self.bs1._internal_points[2].x(), 14.0/3)
        self.assertEqual(self.bs1._internal_points[2].y(), 14.0/3)
        self.assertEqual(self.bs1._internal_points[3].x(), 11.0/2)
        self.assertEqual(self.bs1._internal_points[3].y(), 3)
        self.assertEqual(self.bs1._internal_points[4].x(), 4)
        self.assertEqual(self.bs1._internal_points[4].y(), 1)

        self.bs1._insert_knot(knot=2)
        self.bs1._insert_knot(knot=2)
        new_knotvec = KnotVector([0,0,0,1,2,2,2,3,4,4,4])
        self.assertEqual(self.bs1._internal_knotvec, new_knotvec)
        # assert new points added to right place and old points removed
        self.assertEqual(self.bs1._internal_points[2].polar(), KnotVector([0,1,2]))
        self.assertEqual(self.bs1._internal_points[3].polar(), KnotVector([1,2,2]))
        self.assertEqual(self.bs1._internal_points[4].polar(), KnotVector([2,2,2]))
        self.assertEqual(self.bs1._internal_points[5].polar(), KnotVector([2,2,3]))
        self.assertEqual(self.bs1._internal_points[6].polar(), KnotVector([2,3,4]))
        # assert new points have the right x, y.
        self.assertTrue(float_equals(self.bs1._internal_points[3].x(), 47.0/9))
        self.assertTrue(float_equals(self.bs1._internal_points[3].y(), 32.0/9))
        self.assertTrue(float_equals(self.bs1._internal_points[4].x(), 46.0/9))
        self.assertTrue(float_equals(self.bs1._internal_points[4].y(), 53.0/18))
        self.assertTrue(float_equals(self.bs1._internal_points[5].x(), 5))
        self.assertTrue(float_equals(self.bs1._internal_points[5].y(), 7.0/3))
        self.assertTrue(float_equals(self.bs1._internal_points[6].x(), 4))
        self.assertTrue(float_equals(self.bs1._internal_points[6].y(), 1))


class TestControlPoint(unittest.TestCase):
    def setUp(self):
        self.cp1 = ControlPoint()

    def test_copy(self):
        cp1 = ControlPoint(Point(1, 1), knots=[0,0,0])
        cp2 = cp1.copy()
        self.assertIsNot(cp1, cp2)
        self.assertEquals(cp1, cp2)

        cp1 = ControlPoint()
        cp2 = cp1.copy()
        self.assertIsNot(cp1, cp2)
        self.assertEquals(cp1, cp2)

    def test_cmp(self):
        cp1 = ControlPoint(knots=range(3))
        cp2 = ControlPoint(knots=range(3))
        self.assertTrue(cp1 == cp2)

        cp1 = ControlPoint(knots=[0,0,0])
        cp2 = ControlPoint(knots=[0,0,1])
        self.assertTrue(cp1 < cp2)

        cp1 = ControlPoint(knots=[0,1,2])
        cp2 = ControlPoint(knots=[0,2,3])
        self.assertTrue(cp1 < cp2)
        self.assertTrue(cp2 > cp1)

        cp1 = ControlPoint(knots=[4,4,4])
        cp2 = ControlPoint(knots=[3,4,4])
        self.assertTrue(cp1 > cp2)
    
    def test_interpolate(self):
        cp1 = ControlPoint(Point(1, 1), knots=[0,0,0])
        cp2 = ControlPoint(Point(6, 4), knots=[0,0,1])
        cp3 = ControlPoint(Point(0, 0), knots=[0,0,0.5])

        # a = 0, b = 1, c = 0.5
        # ((b-a) cp1 + (c-a) cp2) / (c-a)
        cp3.interpolate(cp1, cp2)
        self.assertEqual(cp3.x(), 3.5)
        self.assertEqual(cp3.y(), 2.5)

        ############################

        cp1 = ControlPoint(Point(1, 1), knots=[1,1,0])
        cp2 = ControlPoint(Point(6, 4), knots=[0,4,1])
        cp3 = ControlPoint(Point(0, 0), knots=[2,1,0])

        # a = 1, b = 4, c = 2
        # ((b-a) cp1 + (c-a) cp2) / (c-a)
        cp3.interpolate(cp1, cp2)
        self.assertEqual(cp3.x(), 8.0/3)
        self.assertEqual(cp3.y(), 2.0)

        ############################

        cp1 = ControlPoint(Point(1, 1), knots=[0,4,4])
        cp2 = ControlPoint(Point(6, 4), knots=[0,4,8])
        cp3 = ControlPoint(Point(0, 0), knots=[0,5,4])

        # a = 4, b = 8, c = 5
        # ((b-a) cp1 + (c-a) cp2) / (c-a)
        cp3.interpolate(cp1, cp2)
        self.assertEqual(cp3.x(), 3.0/4 * cp1.x() + 1.0/4 * cp2.x())
        self.assertEqual(cp3.y(), 3.0/4 * cp1.y() + 1.0/4 * cp2.y())

    def test_interpolate_with_more_differing_knots(self):
        # Test when there is more than one differing knot in the knot vector.

        cp1 = ControlPoint(Point(1, 1), knots=[0,2,4])
        cp2 = ControlPoint(Point(6, 4), knots=[0,3,8])
        cp3 = ControlPoint(Point(0, 0), knots=[0,5,8])

        self.assertRaises(IllegalKnotVectorException, cp3.interpolate, cp1, cp2)


class TestKnotVector(unittest.TestCase):
    def setUp(self):
        self.kv1 = KnotVector()
        self.kv2 = KnotVector(range(5))
        self.kv3 = KnotVector([3,3,3,4,5,6,6,6])

    def test_is_valid(self):
        self.assertTrue(self.kv1.is_valid())
        self.assertTrue(self.kv2.is_valid())
        self.assertTrue(self.kv3.is_valid())

        kv = KnotVector([1,1,1,0])
        self.assertFalse(kv.is_valid())

        kv = KnotVector([0,1,1,0])
        self.assertFalse(kv.is_valid())

        kv = KnotVector([4,3,2,1])
        self.assertFalse(kv.is_valid())

    def test_insert(self):
        self.kv1.insert(1)
        self.assertEqual(self.kv1.vec, [1])

        self.kv1.insert(1)
        self.assertEqual(self.kv1.vec, [1,1])

        self.kv1.insert(0)
        self.assertEqual(self.kv1.vec, [0,1,1])

        self.kv1.insert(10)
        self.assertEqual(self.kv1.vec, [0,1,1,10])

        self.kv1.insert(5)
        self.assertEqual(self.kv1.vec, [0,1,1,5,10])

        self.kv1.insert(1)
        self.assertEqual(self.kv1.vec, [0,1,1,1,5,10])

    def test_equal(self):
        kv1 = KnotVector()
        kv2 = KnotVector(range(5))
        kv3 = KnotVector([3,3,3,4,5,6,6,6])
        self.assertEqual(self.kv1, kv1)
        self.assertEqual(self.kv2, kv2)
        self.assertEqual(self.kv3, kv3)

    def test_copy(self):
        kv1copy = self.kv1.copy()
        self.assertEqual(kv1copy, self.kv1)
        kv1copy.insert(100)
        self.assertNotEqual(kv1copy, self.kv1)

        kv2copy = self.kv2.copy()
        self.assertEqual(kv2copy, self.kv2)
        kv2copy.insert(0)
        self.assertNotEqual(kv2copy, self.kv2)

        kv3copy = self.kv3.copy()
        self.assertEqual(kv3copy, self.kv3)
        kv3copy.insert(100)
        self.assertNotEqual(kv3copy, self.kv3)

    def test_polar_points(self):
        self.assertEqual(self.kv1.polar_points(), [])
        
        kv2pts = [KnotVector(range(3)),
                  KnotVector(range(1,4)),
                  KnotVector(range(2,5)),
                  KnotVector(range(3,6))]
        pts = self.kv2.polar_points();
        for p1, p2 in zip(pts, kv2pts):
            self.assertEqual(p1, p2)
        
        kv3pts = [KnotVector([3,3,3]),
                  KnotVector([3,3,4]),
                  KnotVector([3,4,5]),
                  KnotVector([4,5,6]),
                  KnotVector([5,6,6]),
                  KnotVector([6,6,6])]
        pts = self.kv3.polar_points();
        for p1, p2 in zip(pts, kv3pts):
            self.assertEqual(p1, p2)

    def test_difference(self):
        kv1 = KnotVector([0,0,0])
        kv2 = KnotVector([0,0,0])
        self.assertEqual(KnotVector.difference(kv1, kv2), None)

        kv1 = KnotVector([0,0,1])
        kv2 = KnotVector([0,0,0])
        self.assertEqual(KnotVector.difference(kv1, kv2), (2, 0))

        kv1 = KnotVector([0,4,4])
        kv2 = KnotVector([0,4,5])
        self.assertEqual(KnotVector.difference(kv1, kv2), (1, 2))

        kv1 = KnotVector([0,1,2])
        kv2 = KnotVector([0,2,2])
        self.assertEqual(KnotVector.difference(kv1, kv2), (1, 1))

        kv1 = KnotVector([1,4,8])
        kv2 = KnotVector([1,8,9])
        self.assertEqual(KnotVector.difference(kv1, kv2), (1, 2))

        kv1 = KnotVector([0, 0, 1])
        kv2 = KnotVector([0, 1, 3])
        kv3 = KnotVector([0, 1, 2])
        self.assertEqual(KnotVector.difference(kv1, kv3), (0, 2))
        self.assertEqual(KnotVector.difference(kv2, kv3), (2, 2))

        kv1 = KnotVector([1,4,8])
        kv2 = KnotVector([1,6,9])
        self.assertRaises(IllegalKnotVectorException, KnotVector.difference, kv1, kv2)

if __name__ == '__main__':
    unittest.main()
