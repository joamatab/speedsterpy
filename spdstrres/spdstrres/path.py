"""_summary_
path.py contains the main algorithms
for the extraction of the central paths
within the IC layout

[author]    Diogo André Silvares Dias
[date]      2022-04-17
[contact]   das.dias@campus.fct.unl.pt
"""
# todo: develop algorithm to detect the 
# binary image bound box

# todo: develop algorithm to convert
# from the image bound box to the gds boundbox

# todo: develop algorithm to compute the 
# central path points of the path from the image skeleton

# todo: develop algorithm to compute the 
# widths of the polygon in each point

# todo: develop algorithm to check if the
# pixel is an end point, a corner point, 
# or an intersection point. IDEAS:
# - check if the pixel is a corner point: neighbours = 2
#                                           and their directions 
#                                           are different, making at 
#                                           least a 135 degree angle
# - check if the pixel is an end point: neighbours = 1
# - check if the pixel is an intersection point: neighbours => 3

# todo: develop the algorithm to compute and return the 
# SpeedsterPath for each input gdspy polygon / path

