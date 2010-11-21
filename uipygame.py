import pygame
import pygame.gfxdraw
pygame.init()

def draw(control_points, draw_points, background_color, point_color, line_color,
        window_w, window_h):
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
