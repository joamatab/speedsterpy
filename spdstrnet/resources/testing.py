import gdspy
ld = {
    "met1": {"layer":1, "datatype": 0},
    "met2": {"layer":2, "datatype": 0}
}
lib = gdspy.GdsLibrary()
cell = lib.new_cell("testing")
polys = [gdspy.Rectangle((0.0,0.0), (1.0,1.0), **ld["met1"])]
polys.append( gdspy.Rectangle( (0.0,0.0),(3.0,1.0), **ld["met2"] ) )
polys.append( gdspy.Polygon( [(0, 0), (1,0), (2,1), (1,3), (0,3), (-1,2)] ) )
for p in polys:
    cell.add(p)
colours = {
    "white": "#FFFFFF",
    "black": "#020202"
}
gdspy.LayoutViewer(lib, background = colours["white"])