Gaining an intuitive understanding for b-splines is difficult without directly
seeing the effects of different knot vectors and control point positions.

Curvey allows you to build b-spline curves by specifying the degree of the
curve, control points, and the knot vector. This allows the user to see b-spline
curves in its most general sense.

Setting Up
=====================

Download:

        https://github.com/eshira/curvey/archives/master

If you like living on the edge, you can download the latest git snapshot:

        $ git clone git://github.com/eshira/curvey.git</div>

Curvey depends on Python an the Tkinter library, which is included in standard
Python distributions. It has been tested on Python 2.6.

Using
=====================

To run the GUI version of Curvey:

        $ python curvey.py --ui

You can also give Curvey an input file:

        $ python curvey.py file
