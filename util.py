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
    is_loading = True
    points = []
    polars = []
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
            polars.append(polar)
        elif line.startswith("degree"):
            degree = line.strip().split('=')
            degree = int(degree[1])
        elif line.startswith("dt"):
            dt = line.strip().split('=')
            dt = float(dt[1])
    is_loading = False
    return points, polars, degree, dt

def mirror_y(points, about_y):
    mirrored = []
    for p in points:
        y = p[1]
        y -= about_y
        y = -y
        y += about_y
        mirrored.append((p[0], y))
    return mirrored

def transform_for_canvas(points, width, height, perpixel_x, perpixel_y):
    halfwidth = width/2
    halfheight = height/2

    transformed = []
    for p in points:
        x = halfwidth + p[0] * perpixel_x
        y = halfheight + p[1] * perpixel_y
        transformed.append((x,y))

    return transformed

