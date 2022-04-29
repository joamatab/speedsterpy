"""_summary_
This script generates the data for performing the tests
of the spdstrnet module
"""

import gdspy
import os

# create a new lib
lib = gdspy.GdsLibrary()
# simple polygon and point
# polygon overlapping
# polygon inclusion (for polygon_contains)
cell = lib.new_cell("test1")
ld = {
    "met1": {"layer":1, "datatype": 0},
    "met2": {"layer":2, "datatype": 0}
}
polys = [gdspy.Rectangle((0.0,0.0), (3.0,1.0), **ld["met1"])]
polys.append( gdspy.Rectangle( (2.0,0.0), (3.0, 3.0), **ld["met2"]) )

polys.append( gdspy.Rectangle( (2.0,0.0), (3.0, 3.0), **ld["met1"]) )

polys.append( gdspy.Rectangle( (.2,.2), (.4, .4), **ld["met1"]) )

# two equal and two different polygons to check if they are the same or not
polys.append( gdspy.Rectangle((0.0,0.0),(3.0,1.0), **ld["met1"]) ) # equal to poly

# rectangle to find the centroid
polys.append( gdspy.Rectangle((0.0,0.0),(1.0,1.0), **ld["met1"]) ) # equal to poly

# polygon and path united to fragment
path = gdspy.Path(1.0, (0.0, 0.0))  # start of path at (0,0), with width of 1 dbu
# build the path vertically, with a length of 4.0
path.segment(4.0, "+y", layer = ld["met1"]["layer"], datatype = ld["met1"]["datatype"])
polys.append(path)

for p in polys:
    cell.add(p)

# observe the created polygons
gdspy.LayoutViewer(lib, background = "#FFFFFF")