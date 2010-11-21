from Tkinter import *
import ScrolledText

class UI:
    default_control_points = """(1, 3)
    (2, 4)
    (6, 5)
    (5, 1)
    (2, 1)
    (0, 2)
    [0,0,0,1,3,4,4,4]
    """
    def __init__(self, control_points, draw_points, background_color, point_color, line_color,
            canvas_w, canvas_h, plane_w=None, plane_h=None):
        self.control_points = control_points
        self.draw_points = draw_points
        self.background_color = background_color
        self.point_color = point_color
        self.line_color = line_color
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.plane_w = plane_w if plane_w else canvas_w
        self.plane_h = plane_h if plane_h else canvas_h

        self.dw = (self.canvas_w - self.plane_w)/2
        self.dh = (self.canvas_h - self.plane_h)/2

        self.master = Tk()
        self.master.title("Curvey")
        self.canvas = Canvas(self.master, width=canvas_w, height=canvas_h, bd=4, background="#cccccc")
        self.canvas.pack()

        self.editbox = Text(self.master, bg='#cccccc', borderwidth=4)
        self.editbox.pack()
        self.editbox.insert('0.0', UI.default_control_points)

        self.renderbutton = Button(self.master, text="Render")
        self.renderbutton.pack()
        #self.renderbutton.bind('<Button-1>', render_callback) # TODO

    def draw(self):

        # Draw control points
        for cp in self.control_points:
            x, y = tuple(cp)
            radius = 4 # pixels
            self.canvas.create_oval(x-radius+self.dw, y-radius+self.dh,
                    x+radius+self.dw, y+radius+self.dh, fill="#ff0000")

        # Draw points
        for i in range(len(self.draw_points)-1):
            x1, y1 = tuple(self.draw_points[i])
            x2, y2 = tuple(self.draw_points[i+1])
            self.canvas.create_line(x1+self.dw, y1+self.dh, x2+self.dw, y2+self.dh, fill="blue")

        mainloop()

