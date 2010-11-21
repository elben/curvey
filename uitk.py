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
            canvas_w=640, canvas_h=320, plane_w=640, plane_h=320):
        self.degree = degree
        self.dt = None
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

        self.editbox = Text(self.master, bg='#cccccc', borderwidth=4)
        self.editbox.pack()
        self.editbox.insert('0.0', UI.default_control_points)

        self.renderbutton = Button(self.master, text="Render")
        self.renderbutton.pack()
        self.renderbutton.bind('<Button-1>', self.render)

        self.clearbutton = Button(self.master, text="Clear")
        self.clearbutton.pack()
        self.clearbutton.bind('<Button-1>', self.clear)

        self.canvas = Canvas(self.master, width=canvas_w, height=canvas_h, bd=4, background="#cccccc")
        self.image = PhotoImage(file='axis.gif')
        self.canvas.create_image(320, 160, image=self.image)
        self.canvas.pack()

    def clear(self, event=None):
        self.canvas.destroy()
        self.canvas = Canvas(self.master, width=self.canvas_w, height=self.canvas_h, bd=4, background="#cccccc")
        self.canvas.create_image(320, 160, image=self.image)
        self.canvas.pack()

    def show(self):
        mainloop()

    def render(self, event=None):
        self.clear()

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

        # Scale and translate points for drawing.
        wrong_control_points, wrong_points = bspline.render()
        control_points = []
        points = []
        for cp in wrong_control_points:
            control_points.append([cp.x(), cp.y()])
        for p in wrong_points:
            points.append([p.x(), p.y()])

        self.control_points = transform_for_canvas(control_points,
                self.plane_w, self.plane_h, 32, 32)
        self.draw_points = transform_for_canvas(points, self.plane_w,
                self.plane_h, 32, 32)

        self.control_points = mirror_y(self.control_points, about_y=160)
        self.draw_points = mirror_y(self.draw_points, about_y=160)

        # Draw.
        self.draw()

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

def main():
    drawui = UI()
    drawui.show()

if __name__ == '__main__':
    main()
