"""_summary_
Script to create a simple layout filled
with interconnected metal shapes 
to proceed to the testing of the features
of the spdstrnet package.
"""

import os
import gdspy
import numpy as np

# The GDSII file is called a library, which contains multiple cells.
lib = gdspy.GdsLibrary()
# Geometry must be placed in cells.
convertion_ratio = 1e-6  # a unit 1 square is a square of 1 um of height and width
cell = lib.new_cell("crossed_metal")
# Create the geometry (a single Rectangle) and add it to the cell.
# ! gdsii file rules
metal = {
    "met1": {"layer": 68, "datatype": 20, "width": 0.160, "min_space": 0.160},
    "via": {"layer": 68, "datatype": 44, "width": 0.160, "min_space": 0.200},
    "met2": {"layer": 69, "datatype": 20, "width": 0.200, "min_space": 0.200},
    "via2": {"layer": 69, "datatype": 44, "width": 0.200, "min_space": 0.200},
    "met3": {"layer": 70, "datatype": 20, "width": 0.200, "min_space": 0.200},
}
lds = {
    key: {"layer": val["layer"], "datatype": val["datatype"]}
    for key, val in metal.items()
}

circuit_w = 10.0  # 10 micrometers of width
circuit_l = 10.0  # 10 micrometers of  length

# * Build the geometry of the layout
polys = []
# ? build metal 1 geometry
# initial point
xi = 0.0
# final point
yplace = True
xf = circuit_l
for y in np.arange(0.0, circuit_w, metal["met1"]["min_space"]):
    if yplace:
        polys.append(
            gdspy.Rectangle((xi, y), (xf, y + metal["met1"]["width"]), **lds["met1"])
        )
    yplace = not (yplace)

# ? build via 1 - 2 geometry
yplace = True
place_via = True
for y in np.arange(0.0, circuit_w, metal["met1"]["min_space"]):
    if yplace:
        xplace = True
        for x in np.arange(0.0, xf, metal["via"]["min_space"]):
            if xplace:
                if place_via:
                    polys.append(
                        gdspy.Rectangle(
                            (x, y),
                            (x + metal["via"]["width"], y + metal["via"]["width"]),
                            **lds["via"],
                        )
                    )
                place_via = not (place_via)
            xplace = not (xplace)
    yplace = not (yplace)

# ? build metal 2 geometry
# initial point
yi = 0.0
# final point
yf = circuit_w + 0.100
# placing semaphore
xplace = True
for x in np.arange(0.0, xf, metal["met2"]["min_space"]):
    if xplace:
        polys.append(
            gdspy.Rectangle((x, yi), (x + metal["met2"]["width"], yf), **lds["met2"])
        )
    xplace = not (xplace)
"""
# ? build via 2 - 3 geometry
xplace = True
for x in np.arange(0.0, circuit_l, metal["met2"]['min_space']):
    if xplace:
        yplace = True
        for y in np.arange(0.0, circuit_w, metal["via2"]['min_space']):
            if yplace:
                polys.append( gdspy.Rectangle((x, y), (x + metal["via2"]['width'] , y + metal["via2"]['width']), **lds["via2"]) )
            yplace = not(yplace)
    xplace = not(xplace)

# ? build metal 3 geometry
# initial point
xi = 0.0
#final point
yplace = True
xf = circuit_l;
for y in np.arange(0.0, circuit_w, metal["met3"]['min_space']):
    if yplace:
        polys.append( gdspy.Rectangle((xi, y), (xf, y + metal["met3"]['width']), **lds["met3"]) )
    yplace = not(yplace)
"""
for p in polys:
    cell.add(p)

dirpath = (
    "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrnet/resources/data"
)
path_gds = os.path.join(dirpath, f"{cell.name}.gds")
path_oas = os.path.join(dirpath, f"{cell.name}.oas")
lib.write_gds(path_gds)
# cell.to_gds(cell.name+'.gds')
gdspy.LayoutViewer(lib)
