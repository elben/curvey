from Tkinter import *
import ScrolledText

default_control_points = """(1, 3)
(2, 4)
(6, 5)
(5, 1)
(2, 1)
(0, 2)
[0,0,0,1,3,4,4,4]
"""
def draw(control_points, draw_points, background_color, point_color, line_color,
        window_w, window_h):
    global default_control_points
    master = Tk()
    master.title("Curvey")
    w = Canvas(master, width=window_w, height=window_h, bd=4, background="#cccccc")
    w.pack()

    editbox = Text(master, bg='#cccccc', borderwidth=4)
    editbox.pack()
    editbox.insert('0.0', default_control_points)

    renderbutton = Button(master, text="Render")
    renderbutton.pack()

    # Draw control points
    for cp in control_points:
        x, y = tuple(cp)
        print "Drawing", x, y
        radius = 4 # pixels
        w.create_oval(x-radius, y-radius, x+radius, y+radius, fill="#ff0000")

    # Draw points
    for i in range(len(draw_points)-1):
        x1, y1 = tuple(draw_points[i])
        x2, y2 = tuple(draw_points[i+1])
        w.create_line(x1, y1, x2, y2, fill="blue")

    mainloop()
