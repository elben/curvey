from Tkinter import *
import ScrolledText
from libcurvey import *
from util import *

class UI:
    _COLOR_BG = "#cccccc"
    _COLOR_CP_FILL = "#ff0000"
    _COLOR_CP_OUTLINE = "#000000"
    _COLOR_CP_TEMP_FILL = "#f5d5dd"
    _COLOR_CP_TEMP_OUTLINE = "#c9a5ae"

    _ERROR_MSG = "Invalid curve specified.\nMake sure you have the right number of points for the degree and knot vector specified."

    def __init__(self, degree=3, canvas_w=640, canvas_h=320):
        self._degree = degree
        self._dt = None
        self._canvas_w = canvas_w
        self._canvas_h = canvas_h

        self._perpixel = 32
        self._radius = 4

        # Data structures

        # Moving control points
        self._moving_cp = -1 # cp being moved
        self._moving_cp_tracer = -1 # cp tracer id

        # Tk Widgets

        self._master = Tk()
        self._master.title("Curvey")

        self._frame = Frame(self._master)

        self._editbox_text = Text(self._frame, bg=UI._COLOR_BG, borderwidth=4, width=20,
                height=30)
        self._editbox_text.insert('0.0', UI.default_control_points)
        
        self._render_button = Button(self._frame, text="Render")

        self._drawing_labels = False
        self._draw_labels_checkbox = Checkbutton(self._frame, text="Control point labels")

        self._clear_button = Button(self._frame, text="Clear")

        self._canvas = Canvas(self._frame, width=canvas_w, height=canvas_h,
                bd=4, background=UI._COLOR_BG)
        self._axis_image = PhotoImage(file='resources/axis.gif')
        self._canvas.create_image(self._canvas_w/2, self._canvas_h/2,
                image=self._axis_image)

        # Bindings.

        self._draw_labels_checkbox.bind('<Button-1>', self._draw_labels_cb)
        self._render_button.bind('<Button-1>', self._render_cb)
        self._clear_button.bind('<Button-1>', self._clear_cb)

        self._canvas.bind('<Button-1>', self._canvas_lclick_cb)
        self._canvas.bind('<Double-Button-1>', self._canvas_2lclick_cb)
        self._canvas.bind('<Button-2>', self._canvas_rclick_cb)
        self._canvas.bind('<Motion>', self._canvas_motion_cb)

        # Grid placements.

        self._frame.grid(row=0, column=0)

        self._editbox_text.grid(row=2, column=0, columnspan=2)
        self._canvas.grid(row=2, column=3, columnspan=2)

        self._draw_labels_checkbox.grid(row=0, column=0, columnspan=2)
        self._render_button.grid(row=1, column=0)
        self._clear_button.grid(row=1, column=1)

    def _canvas_motion_cb(self, event):
        """
        Mouse moved on canvas.
        """
        if not self._is_moving_control_point(): 
            return

        # We're moving a control point, draw a tracer.
        self._canvas.coords(self._moving_cp_tracer, event.x-self._radius,
                event.y-self._radius,
                event.x+self._radius, event.y+self._radius)

    def _canvas_2lclick_cb(self, event):
        """
        Double left click on mouse. Delete a control point.
        """

        closest = self._canvas.find_closest(event.x, event.y)[0]
        self._delete_cp(closest)

    def _canvas_rclick_cb(self, event):
        """
        Right click on mouse. Move a control point.
        """
        self._move_cp(event)

    def _canvas_lclick_cb(self, event):
        """
        Left click on mouse. Add a control point (if none are nearby)
        """

        if self._is_moving_control_point():
            # Place moving control point.
            self._move_cp(event)
        else:
            # Add a control point.
            overlapping = self._canvas.find_overlapping(event.x-self._radius,
                    event.y-self._radius,
                    event.x+self._radius, event.y+self._radius)
            cps = self._canvas.find_withtag('realcp')
            overlapping_cps = set(overlapping).intersection(set(cps))

            if not len(overlapping_cps):
                # No overlapping control points.
                self._create_cp(event.x, event.y)

    def _clear_cb(self, event=None):
        self._clear_lines()
        self._clear_cps()
        self._clear_labels()

    def _draw_labels_cb(self, event=None):
        self._drawing_labels = not self._drawing_labels

    def _render_cb(self, event=None):
        # Grab data.
        s = self._editbox_text.get("0.0", "end")
        lines = s.split('\n')
        text_control_points, knotvec, self._degree, self._dt = parse_data(lines)

        if len(self._canvas.find_withtag('realcp')):
            control_points = self._cp_coords()
            use_text_cps = False
        else:
            control_points = text_control_points
            use_text_cps = True

        # Build BSpline (all in world coordinates).
        bspline = BSpline(degree=self._degree,dt=self._dt)
        for cp in control_points:
            p = ControlPoint(Point(cp[0], cp[1]))
            bspline.insert_control_point(p)
        bspline.replace_knot_vector(knotvec)

        if bspline.is_valid():
            self._clear_lines()
            self._clear_labels()

            # Run de Boor to find spline.
            control_points, control_point_polars, points = bspline.render()

            # Scale and translate points for drawing.
            drawing_control_points = world2canvas(control_points,
                    self._canvas_w, self._canvas_h, self._perpixel)
            drawing_points = world2canvas(points, self._canvas_w,
                    self._canvas_h, self._perpixel)

            # Draw.
            if self._drawing_labels:
                self._draw_labels(drawing_control_points, control_point_polars)
            self._draw_lines(drawing_points)
            if use_text_cps:
                self._draw_control_points(drawing_control_points)

        else:
            if not len(self._canvas.find_withtag('error')):
                self._canvas.create_text(self._canvas_w/2, self._canvas_h/2-100,
                        text=UI._ERROR_MSG, tags=('text','error'))

    def _is_control_point(self, obj):
        tags = self._canvas.gettags(obj)
        return 'realcp' in tags

    def _is_moving_control_point(self):
        return self._moving_cp != -1

    def _create_cp(self, x, y, tags=('cp','realcp'), color=None, outline=None):
        color = color if color else UI._COLOR_CP_FILL
        outline = outline if outline else UI._COLOR_CP_OUTLINE
        oval = self._canvas.create_oval(x-self._radius, y-self._radius,
                x+self._radius, y+self._radius, fill=color, outline=outline, tags=tags)
        return oval

    def _delete_cp(self, obj):
        if self._is_control_point(obj):
            self._canvas.delete(obj)

    def _move_cp(self, event):
        if self._is_moving_control_point():
            # Place control point.
            self._canvas.coords(self._moving_cp,
                    event.x-self._radius, event.y-self._radius,
                    event.x+self._radius, event.y+self._radius)
            self._canvas.itemconfigure(self._moving_cp, fill=UI._COLOR_CP_FILL,
                    outline=UI._COLOR_CP_OUTLINE)
            self._canvas.dtag(self._moving_cp, 'fakecp')
            self._canvas.addtag_withtag('realcp', self._moving_cp)
            self._moving_cp = -1

            # Delete tracer.
            self._canvas.delete(self._moving_cp_tracer)
            self._moving_cp_tracer = -1
        else:
            # Start moving control point.
            closest = self._canvas.find_closest(event.x, event.y)[0]
            if not self._is_control_point(closest):
                return
            self._moving_cp = closest
            coords = self._canvas.coords(closest)

            # Show point as a 'temporary' point
            self._canvas.itemconfigure(closest, fill=UI._COLOR_CP_TEMP_FILL,
                    outline=UI._COLOR_CP_TEMP_OUTLINE)
            self._canvas.dtag(closest, 'realcp')
            self._canvas.addtag_withtag(closest, 'fakecp')

            # Create tracer.
            self._moving_cp_tracer = self._create_cp(event.x, event.y,
                    tags=('cp', 'fakecp'))

    def _cp_coords(self):
        """
        Return the control points draw on screen in world coordinates.
        """
        cps = self._canvas.find_withtag('realcp')
        cps_canvas = map(lambda obj : find_center(*(self._canvas.coords(obj))), cps)
        return canvas2world(cps_canvas, self._canvas_w, self._canvas_h,
                self._perpixel)

    def _clear_cps(self):
        self._canvas.delete('cp')

    def _clear_lines(self):
        self._canvas.delete('line')

    def _clear_labels(self):
        self._canvas.delete('text')

    def _draw_labels(self, cps, polars):
        magic = -10

        for i, cp in enumerate(cps):
            x, y = tuple(cp)
            
            polar = str(polars[i])
            label = "%d %s" % (i, polar)
            self._canvas.create_text(x, y+magic, text=label,
                    tags=('text', 'label'))

    def _draw_control_points(self, cps):
        for i, cp in enumerate(cps):
            x, y = tuple(cp)
            self._create_cp(x, y)

    def _draw_lines(self, drawing_points):
        for i in range(len(drawing_points)-1):
            x1, y1 = tuple(drawing_points[i])
            x2, y2 = tuple(drawing_points[i+1])
            self._canvas.create_line(x1, y1, x2, y2, fill="blue", tags=('line',))

    def show(self):
        mainloop()

    default_control_points = """degree=3
dt=0.2
(1, 3)
(2, 4)
(6, 3)
(5, 1)
(2, 1)
(0, 2)
[0,0,0,1,3,4,4,4]"""



def main(argv):
    drawui = UI()
    drawui.show()

if __name__ == '__main__':
    main([])
