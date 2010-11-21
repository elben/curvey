import sys
import getopt
#import uipygame as ui
import uitk as ui

def parse_data(lines=None, filename=None):
    is_loading = True
    points = []
    polars = []
    degree = 0

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
        elif line[0] == 'd':
            degree = line.strip().split('=')
            degree = int(degree[1])
    is_loading = False
    return points, polars, degree

def flip_points(points, max_y=None):
    if max_y:
        for i in range(len(points)):
            points[i][1] = max_y - points[i][1]
        return max_y

    max_y = -1e100
    for i in range(len(points)):
        if points[i][1] > max_y: max_y = points[i][1]
    for i in range(len(points)):
        points[i][1] = max_y - points[i][1]
    return max_y

def get_draw_points(points, w, h, minmax=None):
    max_x = -1e100
    max_y = -1e100
    min_x = 1e100
    min_y = 1e100

    epsilon = 10

    if not minmax:
        minmax = []
        for p in points:
            x, y = tuple(p)
            if x > max_x: max_x = x
            if x < min_x: min_x = x
            if y > max_y: max_y = y
            if y < min_y: min_y = y
        minmax.append(min_x)
        minmax.append(min_y)
        minmax.append(max_x)
        minmax.append(max_y)
    else:
        min_x = minmax[0]
        min_y = minmax[1]
        max_x = minmax[2]
        max_y = minmax[3]

    max_x -= min_x
    min_x = 0
    max_y -= min_y
    min_y = 0

    # transform points to drawing canvas positions
    #scale_x = w / max_x
    scale_x = 30
    scale_y = scale_x    # currently, we force that scales are equal

    draw_points = []
    for p in points:
        x, y = tuple(p)

        x *= scale_x
        y *= scale_y
        x = x - min_x + epsilon
        y = y - min_y + epsilon

        draw_points.append((x,y))
    return draw_points, minmax

