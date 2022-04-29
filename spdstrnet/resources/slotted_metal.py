"""_summary_
Build a slotted metal shape cell
"""

import os
import gdspy
import numpy as np
# The GDSII file is called a library, which contains multiple cells.
lib = gdspy.GdsLibrary()
# Geometry must be placed in cells.
convertion_ratio = 1e-6 # a unit 1 square is a square of 1 um of height and width
cell = lib.new_cell('slotted_metal')
# Create the geometry (a single Rectangle) and add it to the cell.
# ! gdsii file rules
metal = {
    "met1": {"layer": 68, "datatype": 20, 'width' : 0.160, 'min_space' : 0.160},
    "via":  {'layer' : 68 , 'datatype': 44, 'width' : 0.160, 'min_space' : 0.200},
    "met2": {"layer": 69, "datatype": 20, 'width' : 0.200, 'min_space' : 0.200},
    "via2": {"layer": 69, "datatype": 44, 'width' : 0.200, 'min_space' : 0.200},
    "met3": {"layer": 70, "datatype": 20, 'width' : 0.200, 'min_space' : 0.200},
}
lds = {
    key: {"layer": val["layer"], "datatype": val["datatype"]}
    for key, val in metal.items()
}

circuit_w = 1.21 # 10 micrometers of width
circuit_l = 3.0 # 10 micrometers of  length

polys = []

# ? build horizontal metal 2 geometries
# initial point
xi = 0.0
#final point
yplace = True
xf = circuit_l
for y in np.arange(0.0, circuit_w, metal["met2"]['min_space']):
    if yplace:
        polys.append( gdspy.Rectangle((xi, y), (xf, y + metal["met2"]['width']), **lds["met2"]) )
    yplace = not(yplace)

# ? build vertical metal 2 geometries
# initial y
yi = 0.0
# final y
yf = circuit_w + 0.200
xplace = True
column_width = 0.5
for x in np.arange(0.0, xf + column_width + 0.1, column_width):
    if xplace:
        polys.append(gdspy.Rectangle((x,yi), (x + column_width, yf), **lds["met2"]))
    xplace = not(xplace)

for p in polys:
    cell.add(p)

dirpath = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrnet/resources/data"
path_gds = os.path.join(dirpath, f'{cell.name}.gds')
#path_oas = os.path.join(dirpath, '{}.oas'.format(cell.name))
lib.write_gds(path_gds)
#cell.to_gds(cell.name+'.gds')
gdspy.LayoutViewer(lib)