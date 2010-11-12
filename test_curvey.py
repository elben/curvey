import curvey
import unittest

class TestControlPoitn(unittest.TestCase):
    def setUp(self):
        self.cp1 = curvey.ControlPoint()
    def test_cmp(self):
        cp1 = curvey.ControlPoint(knots=range(3))
        cp2 = curvey.ControlPoint(knots=range(3))
        self.assertTrue(cp1 == cp2)

        cp1 = curvey.ControlPoint(knots=[0,0,0])
        cp2 = curvey.ControlPoint(knots=[0,0,1])
        self.assertTrue(cp1 < cp2)

        cp1 = curvey.ControlPoint(knots=[0,1,2])
        cp2 = curvey.ControlPoint(knots=[0,2,3])
        self.assertTrue(cp1 < cp2)
        self.assertTrue(cp2 > cp1)

        cp1 = curvey.ControlPoint(knots=[4,4,4])
        cp2 = curvey.ControlPoint(knots=[3,4,4])
        self.assertTrue(cp1 > cp2)

class TestKnotVector(unittest.TestCase):
    def setUp(self):
        self.kv1 = curvey.KnotVector()
        self.kv2 = curvey.KnotVector(range(5))
        self.kv3 = curvey.KnotVector([3,3,3,4,5,6,6,6])

    def test_is_valid(self):
        self.assertTrue(self.kv1.is_valid())
        self.assertTrue(self.kv2.is_valid())
        self.assertTrue(self.kv3.is_valid())

        kv = curvey.KnotVector([1,1,1,0])
        self.assertFalse(kv.is_valid())

        kv = curvey.KnotVector([0,1,1,0])
        self.assertFalse(kv.is_valid())

        kv = curvey.KnotVector([4,3,2,1])
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
        kv1 = curvey.KnotVector()
        kv2 = curvey.KnotVector(range(5))
        kv3 = curvey.KnotVector([3,3,3,4,5,6,6,6])
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


if __name__ == '__main__':
    unittest.main()
