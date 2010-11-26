import sys
import getopt
import uitk
import uicmd

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--ui':
        uitk.main(sys.argv)
    elif len(sys.argv) > 1:
        uicmd.main(sys.argv)
    else:
        print "Curvey usage"
        print "1) python curvey.py infile.data"
        print "2) python curvey.py --ui"
