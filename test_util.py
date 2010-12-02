from util import *
import unittest

class TestUtil(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_world2canvas(self):
        points = [(-10, 5),
                (10, -5),
                (0, 0),]
        expected = [(0,0),
                (640, 320),
                (320, 160),]

        transformed = world2canvas(points, 640, 320, 32, 32)
        self.assertEqual(transformed, expected)

    def test_canvas2world(self):
        points = [(0,0),
                (640, 320),
                (320, 160),]
        expected = [(-10, 5),
                (10, -5),
                (0, 0),]

        transformed = canvas2world(points, 640, 320, 32, 32)
        self.assertEqual(transformed, expected)


if __name__ == '__main__':
    unittest.main()
