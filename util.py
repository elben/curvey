import sys

def epsilon_equals(f1, f2, epsilon=0.0001):
    return abs(f1-f2) < epsilon

def epsilon_less_than(f1, f2, epsilon=0.0001):
    return f1 < (f2-epsilon)

def epsilon_less_equal_than(f1, f2, epsilon=0.0001):
    return epsilon_less_than(f1, f2) or epsilon_equals(f1, f2)

def printar(headline, points):
    print
    #print >> sys.stderr, headline
    print headline
    for p in points:
        #print >> sys.stderr, p
        print p

def parse_data(lines=None, filename=None):
    """
    Returns points, polars, degree, and dt.
    points = [[x,y], ...]

    """
    is_loading = True
    points = []
    knotvec = []
    degree = None
    dt = None

    if filename:
        lines = open(filename, 'r')
    for line in lines:
        if len(line) < 1:
            continue
        elif line[0] == '(':
            point = line.strip().strip('()').split(',')
            point = map(float, point)
            points.append(point)
        elif line[0] == '[':
            polar = line.strip().strip('[]').split(',')
            polar = map(float, polar)
            knotvec = polar
        elif line.startswith("degree"):
            degree = line.strip().split('=')
            degree = int(degree[1])
        elif line.startswith("dt"):
            dt = line.strip().split('=')
            dt = float(dt[1])
    is_loading = False

    return points, knotvec, degree, dt

def world2canvas(points, width, height, perpixel_x, perpixel_y):
    """
    Converts from world coordinates to canvas coordinates.

    In canvas coordiantes, (0,0) is at the top-left corner where +x is right and
    +y is down.  In world coordinates, (0,0) is in the middle where +x is right and
    +y is up.
    """
    halfwidth = width/2
    halfheight = height/2

    transformed = []
    for p in points:
        x = p[0] * perpixel_y + halfwidth
        y = halfheight - p[1] * perpixel_y 
        transformed.append((x,y))

    return transformed

def canvas2world(points, width, height, perpixel_x, perpixel_y):
    """
    Converts from canvas coordinates to world coordinates.
    """
    halfwidth = width/2
    halfheight = height/2

    transformed = []
    for p in points:
        x = (p[0] - halfwidth) / perpixel_x
        y = (halfheight - p[1]) / perpixel_y
        transformed.append((x,y))

    return transformed

def find_center(x1, y1, x2, y2):
    return (x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2)
