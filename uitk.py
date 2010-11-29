from Tkinter import *
import ScrolledText
from libcurvey import *
from util import *

class UI:
    default_control_points = """degree=3
dt=0.2
(1, 3)
(2, 4)
(6, 5)
(5, 1)
(2, 1)
(0, 2)
[0,0,0,1,3,4,4,4]"""

    def __init__(self, control_points=None, draw_points=None, degree=3,
            background_color="#cccccc", point_color="#ff0000",
            line_color="#009900",
            canvas_w=640, canvas_h=320):
        self.degree = degree
        self.dt = None
        self.control_points = control_points
        self.control_point_polars = []
        self.draw_points = draw_points
        self.background_color = background_color
        self.point_color = point_color
        self.line_color = line_color
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h

        self.master = Tk()
        self.master.title("Curvey")

        self.frame = Frame(self.master)

        self.editbox = Text(self.frame, bg='#cccccc', borderwidth=4, width=20,
                height=30)
        self.editbox.insert('0.0', UI.default_control_points)
        
        self.renderbutton = Button(self.frame, text="Render")
        self.renderbutton.bind('<Button-1>', self.render_cb)

        self.drawing_labels = False
        self.draw_labels_checkbox = Checkbutton(self.frame, text="Control point labels")
        self.draw_labels_checkbox.bind('<Button-1>', self.draw_labels_cb)

        self.clearbutton = Button(self.frame, text="Clear")
        self.clearbutton.bind('<Button-1>', self.clear_cb)

        self.canvas = Canvas(self.frame, width=canvas_w, height=canvas_h, bd=4, background="#cccccc")
        self.image = PhotoImage(file='axis.gif')
        self.canvas.create_image(320, 160, image=self.image)

        # Grid placements.

        self.frame.grid(row=0, column=0)

        self.editbox.grid(row=2, column=0, columnspan=2)
        self.canvas.grid(row=2, column=3, columnspan=2)

        self.draw_labels_checkbox.grid(row=0, column=0, columnspan=2)
        self.renderbutton.grid(row=1, column=0)
        self.clearbutton.grid(row=1, column=1)

    def clear_cb(self, event=None):
        self.canvas.destroy()
        self.canvas = Canvas(self.frame, width=self.canvas_w, height=self.canvas_h, bd=4, background="#cccccc")
        self.canvas.create_image(320, 160, image=self.image)
        self.canvas.grid(row=2, column=3, columnspan=2)

    def show(self):
        mainloop()

    def draw_labels_cb(self, event=None):
        self.drawing_labels = not self.drawing_labels

    def render_cb(self, event=None):
        self.clear_cb()

        # Grab data.
        s = self.editbox.get("0.0", "end")
        lines = s.split('\n')
        control_points, knotvecs, self.degree, self.dt = parse_data(lines)

        # Build BSpline.
        bspline = BSpline(degree=self.degree,dt=self.dt)
        for cp in control_points:
            p = ControlPoint(Point(cp[0], cp[1]))
            bspline.insert_control_point(p)
        bspline.replace_knot_vector(knotvecs[0])

        if bspline.is_valid():
            # Scale and translate points for drawing.
            control_points, self.control_point_polars, points = bspline.render()

            self.control_points = transform_for_canvas(control_points,
                    self.canvas_w, self.canvas_h, 32, 32)
            self.draw_points = transform_for_canvas(points, self.canvas_w,
                    self.canvas_h, 32, 32)

            self.control_points = mirror_y(self.control_points, about_y=160)
            self.draw_points = mirror_y(self.draw_points, about_y=160)

            # Draw.
            self.draw()
        else:
            error_msg = "Invalid curve specified.\nMake sure you have the right number of points for the degree and knot vector specified."
            self.canvas.create_text(self.canvas_w/2, self.canvas_h/2-100, text=error_msg)

    def draw_labels(self):
        magic = -10

        for i, cp in enumerate(self.control_points):
            x, y = tuple(cp)
            
            polar = str(self.control_point_polars[i])
            label = "%d %s" % (i, polar)
            self.canvas.create_text(x, y+magic, text=label)

    def draw(self):
        # Draw control points
        for i, cp in enumerate(self.control_points):
            x, y = tuple(cp)
            radius = 4 # pixels
            self.canvas.create_oval(x-radius, y-radius,
                    x+radius, y+radius, fill="#ff0000")

        # Draw points
        for i in range(len(self.draw_points)-1):
            x1, y1 = tuple(self.draw_points[i])
            x2, y2 = tuple(self.draw_points[i+1])
            self.canvas.create_line(x1, y1, x2, y2, fill="blue")

        if self.drawing_labels:
            self.draw_labels()

def main(argv):
    drawui = UI()
    drawui.show()

if __name__ == '__main__':
    main([])
