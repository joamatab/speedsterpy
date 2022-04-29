"""_summary_
geometry.py contains the main algorithms
for the preprocessing of layout geometry
in order to enable point to point resistance extraction

[author]    Diogo André Silvares Dias
[date]      2022-04-17
[contact]   das.dias@campus.fct.unl.pt
"""
from loguru import logger
import itertools
from enum import Enum
import warnings
import numpy as np
from gdstk import (
    Library,
    Cell,
    Polygon,
    rectangle,
    RobustPath,
    # functions
    boolean,  # perform boolean operations on two polygon sets
    inside,
)
from .data import (
    SpeedsterPort,
)
from spdstrutil import (
    GdsTable,
    GdsLayerPurpose,
)


class PolygonDirection(Enum):
    """_summary_
    Enum class to define the direction of
    a polygon in relation to its neighbour
    Direction:
        0: no direction
        1: north
        2: north-east
        3: east
        4: south-east
        5: south
        6: south-west
        7: west
        8: north-west
    """

    None
    NORTH = 1  # "+y"
    NORTH_EAST = 2
    EAST = 3  # "+x"
    SOUTH_EAST = 4
    SOUTH = 5  # "-y"
    SOUTH_WEST = 6
    WEST = 7  # "-x"
    NORTH_WEST = 8


def check_point_inside_polygon(
    polygon,
    point: tuple,
) -> bool:
    """_summary_
    Checks if a point is inside a polygon
    Args:
        polygon (Polygon): Polygon Set object
        point   (list)      : [x:float, y: float] items list
    Returns:
        bool: returns wether the point is inside the polygon or not
    """
    if type(point[0]) != float or len(point) != 2:
        raise ValueError("Point must be a tuple of 2 floats.")
    return inside([point], polygon)[0]


def check_polygon_overlap(
    polygonA,
    polygonB,
    layer: int = 0,
    datatype: int = 0,
    precision=1e-3,
) -> list:
    """_summary_
    Checks if two polygons overlap, and
    returns the overlapping region, in case they do
    Args:
        polygonA (Polygon): Polygon object
        polygonB (Polygon): Polygon object
        layer    (int)       : layer of the resulting polygon from the boolean operation
        dataType (int)       : datatype of the resulting polygon from the boolean operation
        precision(float)     : precision of the cuts
    """
    polyList = boolean(
        polygonA, polygonB, "and", layer=layer, datatype=datatype, precision=precision
    )
    return polyList if len(polyList) > 0 else None


def get_common_edges(polyA, polyB) -> list:
    pointsA = polyA.points
    pointsB = polyB.points
    edges = []

    def _superposed_collinear_edge(e1, e2):
        """_summary_
        Checks if two edges e1 and e2 are collinear and intersect
        to infer about their intersection, returning it in case
        it exists
        Args:
            e1 ( array( [p1, p2] ) ): edge1/vector1
            e2 ( array( [p1, p2] ) ): edge2/vector2

        Returns:
            ( array( [p1, p2] ) ) : the superposed edge
        """
        # compute colinearity
        # get 3D vectors defined by e1 and e2
        v1 = [e1[1][0] - e1[0][0], e1[1][1] - e1[0][1], 0]
        v2 = [e2[1][0] - e2[0][0], e2[1][1] - e2[0][1], 0]
        # get cross product
        cp = np.cross(v1, v2)
        norm_cp = np.sqrt(cp.dot(cp))
        # infer colinearity
        if norm_cp != 0.0:  # colinearity exists when |v1xv2| = 0
            return None
        # compute intersection
        # get the straight line defined by e1 : y = ax + b -> y-y0 = a * (x-x0) where a = (y1-y0)/(x1-x0) and b = y0 - a*x0
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # set warnings to error to catch div by zero
            try:
                a = (e1[1][1] - e1[0][1]) / ((e1[1][0] - e1[0][0]))
                b = e1[0][1] - a * e1[0][0]
                # check if the first point of e2 is on top of the straight line defined by the vertices of e1
                if not np.equal(e2[0][1], (a * e2[0][0] + b)):  # y2 == a*x2 + b ?
                    return None
            except Exception:  # division by zero, infinite slope, the defined line is : x = e1[0][0]
                a = None
                # only have to check if the abciss of e2[0] == e1[0][0]
                if not np.equal(e2[0][0], e1[0][0]):
                    return None
        # if it is, check if either the final or the sstarting point of e2 is in the bounding box defined by the vertices of e1
        bbox = rectangle(e1[0], e1[1])
        if not (inside([e2[0]], bbox)[0] or inside([e2[1]], bbox)[0]):
            return None
        # finally, there is actually an intersection, and we must return it
        # check e2 fully contained in e1
        if inside([e2[0]], bbox)[0] and inside([e2[1]], bbox)[0]:
            return e2
        # check for partial intersection
        if inside([e2[0]], bbox)[0]:
            return (e2[0], e1[1])

        if inside([e2[1]], bbox)[0]:
            return (e1[0], e2[1])

        return None

    for edgeA in zip(pointsA, pointsA[1:]):
        for edgeB in zip(pointsB, pointsB[1:]):
            superposed = _superposed_collinear_edge(edgeA, edgeB)
            if superposed is not None:
                edges.append(list(superposed))
        # check last edge
        edgeB = (pointsB[-1], pointsB[0])
        superposed = _superposed_collinear_edge(edgeA, edgeB)
        if superposed is not None:
            edges.append(list(superposed))
    # LAST ITERATION
    # check last edge
    edgeA = (pointsA[-1], pointsA[0])
    for edgeB in zip(pointsB[:-1], pointsB[1:]):
        superposed = _superposed_collinear_edge(edgeA, edgeB)
        if superposed is not None:
            edges.append(list(superposed))
    # check last edge
    edgeB = (pointsB[-1], pointsB[0])
    superposed = _superposed_collinear_edge(edgeA, edgeB)
    if superposed is not None:
        edges.append(list(superposed))
    # convert edges to list of tuples and filter the edges defining a single point
    edges = [
        [tuple(p) for p in edge]
        for edge in edges
        if not np.array_equal(edge[0], edge[1])
    ]
    return edges if len(edges) > 0 else None


def bool_polygon_overlap_check(polygonA, polygonB, lock=False) -> bool:
    """_summary_
    Performs a boolean check
    to infer if the two polygons overlap
    Args:
        polygonA (Polygon): Polygon object
        polygonB (Polygon): Polygon object
    Returns:
        bool:   returns wether the two polygons overlap or not
                True: They overlap; False: They don't overlap
    """
    return check_polygon_overlap(polygonA, polygonB) is not None


def check_neighbour_polygons(
    polyA,
    polyB,
) -> bool:
    """_summary_
    Checks if the two polygons have common edges and don't overlap!
    Args:
        polygonA (Polygon): Polygon object
        polygonB (Polygon): Polygon object
    Returns:
        bool:   returns wether the two polygons have common edges
                True: They have common edges; False: They don't have common edges
    """
    if (
        polyA.layer == polyB.layer
        and polyA.datatype == polyB.datatype
        and get_common_edges(polyA, polyB) is not None
    ):
        return not bool_polygon_overlap_check(polyA, polyB)
    return False


def check_same_polygon(
    polyA,
    polyB,
    precision=1e-3,
) -> bool:
    """_summary_
    Checks if two polygons are the same
    Args:
        polyA       (np.array)  : vertices of the polygon
        polyB       (np.array)  : vertices of the polygon
        precision   (float)     : precision of the comparison
    Returns:
        bool: returns wether the two polygons are the same or not
                True : They are the same; False: They are not the same
    """

    # check if the layers and datatype are the same
    if polyA.layer != polyB.layer:
        return False
    layer = polyA.layer
    if polyA.datatype != polyB.datatype:
        return False
    datatype = polyA.datatype
    # check if the interception of the two polygons is equal to both of them, or
    # if the not operation (polyA - polyB) and (polyB - polyA) is equal to an empty space of points/polygons
    notAB = boolean(polyA, polyB, "not")
    notBA = boolean(polyB, polyA, "not")
    return len(notAB) == 0 and len(notBA) == 0


def check_polygon_contains_polygon(
    polyA,
    polyB,
) -> bool:
    """_summary_
    Checks if polygon A contains polygon B
    Args:
        polyA       (np.array)  : vertices of the polygon
        polyB       (np.array)  : vertices of the polygon
        maxPoints   (int)       : maximum number of points inside the polygon
        precision   (float)     : precision of the comparison
    Returns:
        bool: returns wether polygon A contains polygon B or not
                True : polygon A contains polygon B; False: polygon A doesn't contain polygon B
    """
    # check if the layers and datatype are the same
    if polyA.layer != polyB.layer:
        return False
    if polyA.datatype != polyB.datatype:
        return False
    # if the union of the two polygons is equal to the polygon A, then polygon A contains polygon B
    # which is equal to checking if : (polyA U polyB) NOT polyA == 0
    unionAB = boolean(polyA, polyB, "or", layer=polyA.layer, datatype=polyA.datatype)
    boolMap = [check_same_polygon(uniAB, polyA) for uniAB in unionAB]
    return (False not in boolMap) or check_same_polygon(polyA, polyB)


def find_centroid(
    poly: np.array,
) -> list:
    """_summary_
    Finds the centroid of a single polygon
    Args:
        poly (np.array): vertices of the polygon
    Returns:
        list: [x:float, y: float] 2 items list
    """
    cent = [0, 0]
    nPoly = len(poly)
    signedArea = 0.0
    # for all the vertices of the polygon
    for k, point in enumerate(nPoly):
        x0 = point[0]
        y0 = point[1]
        opposite_point = poly[(k + 1) % nPoly]
        x1 = opposite_point[0]
        y1 = opposite_point[1]
        # compute the value of the area composed of the two vertices
        # using the shoelace formula
        A = x0 * y1 - x1 * y0
        signedArea += A
        # compute the centroid's coordinates
        cent[0] += (x0 + x1) * A
        cent[1] += (y0 + y1) * A
    # compute the centroid's coordinates
    signedArea *= 0.5
    cent[0] = cent[0] / (6.0 * signedArea)
    cent[1] = cent[1] / (6.0 * signedArea)
    return cent


def unit_vec(
    pointA: list,
    pointB: list,
) -> list:
    """_summary_
    Returns the unit vector of a point
    Args:
        point (list) : [x:float, y: float] 2 items list
    Returns:
        list: [x:float, y: float] 2 items list
    """
    vec: list = [pointB[0] - pointA[0], pointB[1] - pointA[1]]
    return [vec[0] / np.linalg.norm(vec), vec[1] / np.linalg.norm(vec)]


def saturate_vector(vec: list) -> list:
    """_summary_
    Saturates a vector to a unit vector
    Args:
        vec (list): [vx:float, vy: float] the vector to saturate
    Returns:
        list: [vx, vy] the saturated vector
    """
    vx = 1 if vec[0] >= 0.5 else (-1 if vec[0] < -0.5 else 0)
    vy = 1 if vec[1] >= 0.5 else (-1 if vec[1] < -0.5 else 0)
    return [vx, vy]


def check_neighbour_direction(
    poly: np.array,
    neighbour: np.array,
) -> PolygonDirection:
    """_summary_
    In case the polygon intercepts
    its neighbour, returns the direction
    in which it happens
    Args:
        poly        (np.array): vertices of the polygon
        neighbour   (np.array): vertices of the neighbour
    Returns:
        PolygonDirection: the direction in which the polygon intercepts
    """
    # check if the polygon and its neighbour intersect
    if not bool_polygon_overlap_check(poly, neighbour):
        # if they don't, return no direction
        return None
    # if they do,
    # compute the centers of each polygon, assuming both are squares and convex hulls
    center1 = find_centroid(poly)
    center2 = find_centroid(neighbour)
    # from the center point of the polygons,
    # check the direction of the neighbour , in relation to the polygon
    direction_vec = unit_vec(center1, center2)
    # saturate the direction in North, South, East, West
    direction = saturate_vector(direction_vec)
    # return the direction
    if direction == [0, 1]:
        return PolygonDirection.NORTH
    elif direction == [0, -1]:
        return PolygonDirection.SOUTH
    elif direction == [1, 0]:
        return PolygonDirection.EAST
    elif direction == [-1, 0]:
        return PolygonDirection.WEST
    elif direction == [1, 1]:
        return PolygonDirection.NORTH_EAST
    elif direction == [-1, 1]:
        return PolygonDirection.NORTH_WEST
    elif direction == [1, -1]:
        return PolygonDirection.SOUTH_EAST
    elif direction == [-1, -1]:
        return PolygonDirection.SOUTH_WEST
    else:
        return None


def get_direction_between_rects(
    poly: np.array,
    neighbour: np.array,
) -> PolygonDirection:
    """_summary_
    Gets the direction between two rectangles!
    Args:
        poly        (np.array): from rectangle
        neighbour   (np.array): to rectangle
    Returns:
        PolygonDirection: direction between the rectangles
    """
    if len(poly) != 4 or len(neighbour) != 4:
        raise ValueError("rectangles must have 4 vertices only!")
    # get the 8-side direction between the two rectangles
    direction = check_neighbour_direction(poly, neighbour)
    # check which side (horizontal or vertical) is the bigger
    verd = np.max(list(poly[:, 1])) - np.min(list(poly[:, 1]))
    hord = np.max(list(poly[:, 0])) - np.min(list(poly[:, 0]))
    retDir = direction
    if verd > hord:
        if retDir in [PolygonDirection.NORTH_EAST, PolygonDirection.NORTH_WEST]:
            retDir = PolygonDirection.NORTH
        elif retDir in [PolygonDirection.SOUTH_EAST, PolygonDirection.SOUTH_WEST]:
            retDir = PolygonDirection.SOUTH
    elif retDir in [PolygonDirection.NORTH_EAST, PolygonDirection.SOUTH_EAST]:
        retDir = PolygonDirection.EAST
    elif retDir in [PolygonDirection.SOUTH_WEST, PolygonDirection.NORTH_WEST]:
        retDir = PolygonDirection.WEST
    return retDir


def fragment_polygon(
    poly: Polygon,
    maxPoints=199,
    precision=1e-3,
) -> Polygon:
    """_summary_
    #! Deprecated
    Fragments the polygon into a Polygon object
    Args:
        poly        (Polygon)   : the polygon to fragment
        maxPoints   (int)       : the maximum number of points to keep
        precision   (float)     : the precision to use
    Returns:
        Polygon: the polygon set resulting from the fragmentation operation
    """
    raise DeprecationWarning("This function is deprecated!")
    # return poly.fracture(max_points = maxPoints, precision = precision)


def fragment_net(
    name: str,
    cell: Cell,
    maxPoints=199,
    precision=1e-3,
) -> Cell:
    """_summary_
    Fragments the net into a Cell of Polygon
    objects resulting from horizontal and vertical
    cuts in each polygon, and returns it
    Args:
        name        (str)       : the name of the cell
        cell        (Cell)   : Cell object containing the net
        maxPoints   (int)       : maximum number of points inside the polygon
        precision   (float)     : precision of the cuts
    """
    # create a new gds cell, to which the fragments will be added
    net = Cell(name, exclude_from_current=True)
    for (poly, path, label, references) in cell:
        net.add(fragment_polygon(poly, maxPoints, precision))
        net.add(fragment_polygon(path, maxPoints, precision))
        net.add(label)
        net.add(references)
    return net


def get_polygons_by_spec(
    cell: Cell,
    layer,
    datatype,
) -> list:
    return [
        poly
        for poly in itertools.chain(cell.get_polygonsets(), cell.get_paths())
        if poly.layers[0] == layer and poly.datatypes[0] == datatype
    ]


def get_polygon_dict(
    cell: Cell,
    specs: list,
) -> dict:
    """_summary_
    Gets a dictionary of polygons by spec
    Args:
        cell        (Cell)   : Cell object containing the net
        spec        (list)      : list of layer, datatype and name
    Returns:
        dict: dictionary of {(layer,datatype): [polygons]}
    """
    ret = {}
    if not specs:
        return ret
    if type(specs[0]) != tuple or type(specs[0]) != list and len(specs[0]) != 2:
        raise TypeError(
            "The specifications must be a list of tuples or lists of length 2!"
        )
    for spec in specs:
        layer = spec[0]
        datatype = spec[1]
        if (layer, datatype) in ret:
            raise ValueError("The specifications must be unique!")
        ret[(layer, datatype)] = get_polygons_by_spec(cell, layer, datatype)
    return ret


def check_polygon_in_cell(
    polygon,
    cell: Cell,
) -> bool:
    """_summary_
    Checks if a polygon is inside a cell already
    Args:
        polygon (_type_): _description_
        cell (Cell): _description_

    Returns:
        bool: _description_
    """
    # check if the received polygons are valid
    if type(polygon) not in [Polygon, rectangle, RobustPath]:
        raise TypeError(
            "polyA must be a Polygon, Polygon, rectangle or RobustPath object!"
        )
    layer = polygon.layers[0]
    datatype = polygon.datatypes[0]
    return any(
        check_same_polygon(polygon, other)
        for other in get_polygons_by_spec(cell, layer, datatype)
    )


def check_via_connection(polyA, via, polyB) -> bool:
    """_summary_
    Checks if the polygon A and B are connected through
    the specified via
    Args:
        polyA   (Polygon): polygon in metal layer above
        via     (Polygon): polygon in metal layer between
        polyB   (Polygon): polygon in metal layer below
    Returns:
        bool: True if the polygons are connected through the via
                False otherwise
    Notes:
        # ! This function assumes that the polygons A, via and B
        # ! are in three consecutive gds layers! If they are not, the provided
        # ! result will not mean anything
    """
    # check if the received polygons are valid
    if type(polyA) not in [Polygon, rectangle, RobustPath]:
        raise TypeError(
            "polyA must be a Polygon, Polygon, rectangle or RobustPath object!"
        )
    if type(polyB) not in [Polygon, rectangle, RobustPath]:
        raise TypeError(
            "polyB must be a Polygon, Polygon, rectangle or RobustPath object!"
        )
    if type(via) not in [Polygon, rectangle, RobustPath]:
        raise TypeError(
            "via must be a Polygon, Polygon, rectangle or RobustPath object!"
        )
    # check if the polygons are the same in pairs
    if check_same_polygon(polyA, polyB):
        return False
    if check_same_polygon(polyA, via):
        return False
    if check_same_polygon(polyB, via):
        return False

    # check if the layers are not the same
    if polyA.layers[0] == polyB.layers[0]:
        return False
    if polyA.layers[0] == via.layers[0]:
        return False
    if polyB.layers[0] == via.layers[0]:
        return False
    # finally , check for mutual overlap of vias by the two polygons
    return bool_polygon_overlap_check(polyA, via) and bool_polygon_overlap_check(
        polyB, via
    )


def join_overlapping_polygons_cell(
    cell: Cell,
    layerMap: dict,
) -> Cell:
    """_summary_
    Joins overlapping the overlapping polygons for each metal
    layer of a gds cell (resembling a layout), in order to
    join multiple intercepting polygons in a single polygon.
    Args:
        cell        (Cell)  : the gdspy.Cell object
        layerMap    (dict)  : dictionary of {"layer name": (layer, datatype)} tuples
    Returns:
        Cell: the new gdspy.Cell object with the joined polygons
    """
    newCell = Cell(f"{cell.name}_joined", exclude_from_current=True)
    polygons = cell.get_polygons(by_spec=list(layerMap.values()))
    for layer, datatype in polygons.keys():
        poly = boolean(
            polygons[(layer, datatype)],
            polygons[(layer, datatype)],
            "or",
            layer=layer,
            datatype=datatype,
        )
        poly = Polygon(poly, layer=layer, datatype=datatype)
        newCell.add(poly)
    return newCell


def fuse_overlapping_cells(
    cellA: Cell,
    cellB: Cell,
    maxPoints: int = 199,
    precision: float = 1e-3,
) -> Cell:
    """_summary_
    Fuses both cells into a single cell if both cells
    have at least one polygon of any layer in common
    Args:
        cellA       (Cell): gdspy Cell object
        cellB       (Cell): gdspy Cell object
        maxPoints   (int, optional): Maximum number of points inside polys when uniting cells. Defaults to 199.
        precision (float, optional): Precision of the cuts when performing union of cells.Defaults to 1e-3.

    Returns:
        Cell: Cells resulting from the union of cellA and cellB
        None: If no polygon of any layer in common
    """
    # get the layers that are common to both cells
    layersA = cellA.get_layers()
    datatypesA = cellA.get_datatypes()
    ldA = list(zip(layersA, datatypesA))
    layersB = cellB.get_layers()
    datatypesB = cellB.get_datatypes()
    ldB = list(zip(layersB, datatypesB))
    commonLd = [
        ld for ld in ldA if ld in ldB
    ]  # get the common layer,datatype tuples to both cells
    for layer, datatype in commonLd:
        for polyA in get_polygons_by_spec(cellA, layer, datatype):
            if check_polygon_in_cell(polyA, cellB):
                # fuse the cells together and return it
                fuseCell = cellA.copy(cellA.name)
                [fuseCell.add(item) for item in cellB]
                return fuseCell
    return None


def select_abstraction_depth(
    name: str, lib: Library, depth: int = 0, select: dict = {}
) -> Library:
    """_summary_
    Extracts the selected layers of the
    cells of the library at a given
    abstraction depth, and returns a new Library
    Args:
        name   (str)        : name of the returning library
        lib    (Library) : Library object to be extracted from
        depth  (int)        : abstraction depth
        select (dict)       : dictionary of selected (layer, datatype) tuples
    """
    # create a new library
    newLib = Library(name)
    for cell in lib:
        # create a new cell
        newCell = Cell(cell.name, exclude_from_current=True)
        # add the polygons, paths, labels to the new cell
        newCell.add(cell.get_polygons(depth=depth))
        newCell.add(cell.get_polygonsets(depth=depth))
        newCell.add(cell.get_paths(depth=depth))
        newCell.add(cell.get_labels(depth=depth))
        # don't add the references
        # add the cell to the new library
        newLib.add(newCell)
    return newLib


def add_port(
    port: SpeedsterPort,
    layout: Cell,
    table: GdsTable,
) -> None:
    """_summary_
    Adds/Draws a port to the a layout cell
    Args:
        port    (SpeedsterPort) : SpeedsterPort object
        layout  (Cell)       : a gdspy Cell object containing the layout
                                    to which the port will be added
    """
    layer, datatype = table.getGdsLayerDatatypeFromLayerNamePurpose(
        port.layer, GdsLayerPurpose(port.purpose)
    )[0]
    portPoly = Polygon(port.get_polygon(), layer, datatype)
    layout.add(portPoly)
