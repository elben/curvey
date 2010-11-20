import sys
import getopt
import pygame
import pygame.gfxdraw
pygame.init()

max_x = -1e100
max_y = -1e100
min_x = 1e100
min_y = 1e100

def parse_data(filename):
    global max_x, max_y, min_x, min_y
    is_loading = True
    points = []
    polars = []

    f = open(filename, 'r')
    for line in f:
        if line[0] == '(':
            point = line.strip().strip('()').split(',')
            point = map(float, point)
            if point[0] > max_x: max_x = point[0]
            if point[1] > max_y: max_y = point[1]
            if point[0] < min_x: min_x = point[0]
            if point[1] < min_y: min_y = point[1]
            points.append(point)
        elif line[0] == '[':
            polar = line.strip().strip('[]').split(',')
            polar = map(float, point)
            polars.append(point)
    is_loading = False
    return points, polars

def get_draw_points(points, w, h):
    # transform points to drawing canvas positions
    translate_x = min_x
    translate_y = min_y
    scale_x = w / max_x
    scale_y = h / max_y

    draw_points = []
    for p in points:
        x, y = tuple(p)

        x -= translate_x
        x *= scale_x
        y -= translate_y
        y *= scale_y

        # the canvas starts at top-left, so we need to flip our points
        y = h - y
        draw_points.append((x,y))
    return draw_points

def main():
    background_color = (255,255,255)
    line_color = (0,128,0)
    point_color = (128,0,0)

    control_points, knotvec = parse_data(sys.argv[1])
    points, polars = parse_data(sys.argv[2])

    window_w, window_h = 640.0, 480.0
    w, h = window_w - 40.0, window_h - 40.0
    draw_points = get_draw_points(points, w, h)
    control_points = get_draw_points(control_points, w, h)

    #create the screen
    window = pygame.display.set_mode((window_w, window_h)) 
    window.fill(background_color)

    # draw control points
    for cp in control_points:
        pygame.gfxdraw.aacircle(window, int(cp[0]), int(cp[1]), 4, point_color)

    # draw line segments
    pygame.draw.aalines(window, line_color, False, draw_points, 1)
    pygame.display.flip() 

    while True: 
       for event in pygame.event.get(): 
          if event.type == pygame.QUIT: 
              sys.exit(0) 
          #else: 
              #print event 

if __name__ == '__main__':
    main()
