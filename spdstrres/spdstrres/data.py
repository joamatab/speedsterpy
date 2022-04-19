"""_summary_
data.py contains the main data structures and
classes for the performance of the resistance
extraction method leveraged by image processing

[author]    Diogo André Silvares Dias
[date]      2022-04-17
[contact]   das.dias@campus.fct.unl.pt
"""
from enum import Enum
import numpy as np
import sys
sys.path.append("../spdstrutil")
from spdstrutil import Unimplemented
from gdspy import (
    Path,
    Polygon,
)
class SpeedsterPointType(Enum):
    """_summary_
    SpeedsterPointType enum
    Args:
        None
        INPUT : input point
        OUTPUT : output point
        IO: input and output point
    """
    None
    INPUT = 1
    OUTPUT = 2
    IO = 3
    

# TODO : Develop a SpeedsterPoint class
# to allow for the representation of points
# telling the tool if it is an output or input of current
# the resistance of the point, and if it is a 
# corner/interconnection or an end point of the path.
class Point(object):
    __slots__ = [
        'x',
        'y',
        'ioType',
        'resistance',
    ]
    def __init__(
        self, 
        x:float = 0.0, 
        y:float = 0.0, 
        ioType: SpeedsterPointType = None, 
        resistance = None,
    ):
        self.x = x
        self.y = y
        self.ioType = ioType
        self.resistance = resistance
    
    def __str__(self):
        ret  = "{} {} ".format(self.x, self.y)
        ret += "Type: {} ".format(self.ioType.name)
        ret += "R[ohm]: {} ".format(self.resistance)
        return ret
    
    def __dict__(self):
        """_summary_
        Returns a dictionary representation of the point
        """
        return {
            'x': self.x,
            'y': self.y,
            'ioType': self.ioType.name,
            'resistance': self.resistance,
        }
        
    def parseData(self, yamlDict: dict):
        """_summary_
        Parses the data of a point
        Args:
            data (dict): a dictionary containing the data
        """
        self.x = yamlDict['x']
        self.y = yamlDict['y']
        self.ioType = SpeedsterPointType[yamlDict['ioType']]
        self.resistance = yamlDict['resistance']

    def setResistance(self, resistance = 0.0):
        """_summary_
        Sets the resistance of the point
        """
        if type(resistance) is not float:
            raise TypeError("Resistance must be a float")
        self.resistance = resistance

    def setIO(self, ioType: SpeedsterPointType = None):
        """_summary_
        Sets the type of the point
        """
        self.ioType = ioType
        
    def isInput(self) -> bool:
        """_summary_
        Returns if the point is an input point
        """
        return self.ioType == SpeedsterPointType.INPUT \
            or self.ioType == SpeedsterPointType.IO
    
    def isOutput(self) -> bool:
        """_summary_
        Returns if the point is an output point
        """
        return self.ioType == SpeedsterPointType.OUTPUT \
            or self.ioType == SpeedsterPointType.IO
    
    def __add__(self, other):
        """_summary_
        Adds two points
        """
        if type(other) is not Point:
            raise TypeError("other must be a Point")
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """_summary_
        Subtracts two points
        """
        if type(other) is not Point:
            raise TypeError("other must be a Point")
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar = 1.0):
        """_summary_
        Multiplies two points
        """
        if type(scalar) is not float:
            raise TypeError("scalar must be a float")
        return Point(self.x * scalar, self.y * scalar)

    def __eq__(self, other: object) -> bool:
        """_summary_
        Returns if two Speedster Paths are equal
        Args:
            other (object): a generic Python object
        """
        if type(other) is not Point:
            raise TypeError("other must be a Point")
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: object) -> bool:
        """_summary_
        Returns if two Speedster Paths are not equal
        Args:
            other (object): a generic Python object
        """
        return not self.__eq__(other)
class SpeedsterPath(object):
    """_summary_
    Speedster's core geometric data structure
    to save the central path representation of any
    generic GDS polygon 
    Args:
        object (_type_): _description_
    """
    __slots__ = [
        "points",
        "widths",
        "fixMap"
    ]
    def __init__(self, points = [], widths = [], fixMap = []):
        """_summary_

        Args:
            points (list, optional): list of points of the central path points. Defaults to [].
            widths (list, optional): list of widths for each central path point. Defaults to [].
            fixMap (list, optional): boolean map indicating if a point is 
                                        at a corner, intersection, or end node (or not). Defaults to [].
        Raises:
            TypeError: _description_
            TypeError: _description_
        """
        if points != []:
            if type(points[0]) != list :
                raise TypeError("A list of [x coord, y coord] must be parsed in points")
        if widths != []:
            if type(widths[0]) != float:
                raise TypeError("The parsed widths must be a list of floating point numbers")   
        self.points = np.array( [ np.array(p) for p in points ] )    
        self.widths = np.array( widths )
        self.fixMap = np.array( fixMap )
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self) -> str:
        return str(self.__dict__())
    
    def __getitem__(self, index: int) -> list:
        """_summary_
        Returns a point of the Speedster Path geometry data structure
        Args:
            index (int): index of the point to be returned
        """
        return self.points[index]
    
    def __iter__(self):
        """_summary_
        Returns an iterator for the points of the
        Speedster Path geometry data structure
        """
        return self.points.__iter__()
    
    def __eq__(self, other: object) -> bool:
        """_summary_
        Returns if two Speedster Paths are equal
        Args:
            other (object): a generic Python object
        """
        if not isinstance(other, SpeedsterPath):
            return False
        if not np.array_equal(self.points, other.points):
            return False
        if not np.array_equal(self.widths, other.widths):
            return False
        if not np.array_equal(self.fixMap, other.conerMap):
            return False
        return True
    
    def __ne__(self, other: object) -> bool:
        """_summary_
        Returns if the Speedster Path geometry data structure is not equal to another
        Args:
            other (object): _description_
        """
        return not self.__eq__(other)
    
    def __dict__(self) -> dict:
        """_summary_
        Return a dict representation of the Speedster Path
        geometry data structure.
        """
        newDict = {"path":{"points":[], "widths":[], "corner": []}}
        newDict["path"]["points"] = [ list(p) for p in self.points ]
        newDict["path"]["widths"] = list(self.widths)
        newDict["path"]["corner"] = list(self.fixMap)
        return newDict
    
    def parseData(self, yamlDict: dict) -> None:
        """_summary_
        Auto-generate the Speedster Path geometry data structure
        from a given yaml recovered dict
        Args:
            yamlDict (dict): a dictionary containing the Speedster Path
                             geometry data structure
        """
        if not "path" in yamlDict:
            raise TypeError("The parsed yamlDict must contain the \"path\" key")
        if not "points" in yamlDict["path"]:
            raise TypeError("The parsed yaml dict must contain a 'path' with 'points'")
        self.points = np.array( [ np.array(p) for p in yamlDict["path"]["points"] ] )
        if not "widths" in yamlDict["path"]:
            raise TypeError("The parsed yaml dict must contain a 'path' with 'widths'")
        self.widths = np.array( yamlDict["path"]["widths"] )
        if not "corner" in yamlDict["path"]:
            raise TypeError("The parsed yaml dict must contain a 'path' with 'corner'")
        self.fixMap = np.array( yamlDict["path"]["corner"] )
        
    def add(self, point:list, width:float) -> None:
        """_summary_
        Add a point to the Speedster Path geometry data structure
        Args:
            point (list): _description_
            width (float): _description_
        """
        np.append(self.points, [point], axis=0)
        np.append(self.widths, width)
    
    def offset(self, dx = 0.0, dy = 0.0) -> None:
        """_summary_
        Offsets the Speedster Path geometry data structure
        Args:
            dx (float, optional): x axis offset. Defaults to 0.0.
            dy (float, optional): y axis offset. Defaults to 0.0.
        """
        self.points += np.array([dx, dy])
    
    def boundingBox(self) -> list:
        """_summary_
        Returns the bounding box of the Speedster Path geometry data structure
        Returns:
            list: [ [xmin, ymin], [xmax, ymax]]
        """
        return [
            [
                np.min(self.points[:,0]),
                np.min(self.points[:,1])
            ],
            [
                np.max(self.points[:,0]),
                np.max(self.points[:,1])
            ]
        ]
    
    def isFixed(self, point:list) -> bool:
        """_summary_
        Returns if a point is a corner/intersection or not
        Args:
            point (list): _description_
        """
        return self.fixMap[self.points == np.array(point)]
    
    
    def reduceResolution(self, factor: int = 1) -> None:
        """_summary_
        Reduces the resolution of the points
        belonging to the Speedster Path data structure
        Args:
            factor (int) : the number of points successive points
                            to remove during the reduction
        """
        cnt = 0
        keep = np.ones(len(self.points), dtype=bool)
        for i in range(len(self.points)):
            if cnt != factor:
                cnt += 1
            else:
                cnt = 0
                if not self.isFixed(self.points[i]):
                    # if points is not a corner, don't keep it
                    keep[i] = False
                # if point is a corner, we must keep it!
        # keep only the points that are corners and 
        # the points that are left behind after the reduction
        self.points = self.points[keep]
        self.widths = self.widths[keep]
        self.fixMap = self.fixMap[keep]
    
    def fromPath(self, path: Path) :
        """_summary_
        Constructs a Speedster Path from a gdspy Path
        Args:
            path (gdspy.Path): gdsii Path object
        """
        self.points = np.array( [ Point(p[0], p[1]) for p in path.points ] )
        self.widths = np.array( path.width )
        self.fixMap = np.zeros( len(self.points), dtype=bool )
        # signal the first and last points (end nodes) as irremovable
        self.fixMap[0] = True
        self.fixMap[-1] = True
    
    def fromPolygon(self, poly: Polygon) -> Unimplemented:
        """_summary_
        Constructs a Speedster Path from a gdspy Polygon
        Args:
            poly (gdspy.Polygon): gdsii Polygon object
        """
        # requires the use of core image processing algorithms
        return Unimplemented("SpeedsterPath.from_polygon : Not implemented yet.") 


#TODO : Develop a SpeedsterCell to save the
# Speedster representation of the layout geometries
class SpeedsterCell(object):
    def __init__(self) -> Unimplemented:
        """_summary_
        Constructs a Speedster Cell
        """
        return Unimplemented("SpeedsterCell: Not implemented yet.")
    
class SpeedsterResMap(object):
    """_summary_
    Standard resistance map data structure
    for the Speedster tool
    """
    __slots__ = [
        "r"
    ]
    
    def __init__(self, resistances = []):
        if resistances != []:
            if type(resistances[0]) != float:
                raise TypeError("The resistances must be a list of floats")
        self.r = np.array(resistances)
    
    def __dict__(self) -> dict:
        return {"r": list(self.r)}
    
    def __eq__(self, other) -> bool:
        """_summary_
        Returns if the Speedster ResMap geometry data structure is equal to another
        Args:
            other (object): _description_
        """
        if type(other) != SpeedsterResMap:
            return False
        return np.array_equal(self.r, other.r)
    
    def __ne__(self, other) -> bool:
        """_summary_
        Returns if the Speedster ResMap geometry data structure is not equal to another
        Args:
            other (object): _description_
        """
        return not self.__eq__(other)
    
    def __str__(self) -> str:
        return str(self.r)
    
    def __repr__(self) -> str:
        return str(self.r)
    
    def __len__(self) -> int:
        return len(self.r)
    
    def __getitem__(self, index: int) -> float:
        return self.r[index]
    
    def __iter__(self) -> iter:
        return iter(self.r)

    def __setitem__(self, index: int, value: float) -> None:
        self.r[index] = value
        
    def __delitem__(self, index: int) -> None:
        del self.r[index]
    
    def __append__(self, value: float) -> np.array:
        self.r = np.append(self.r, value)
        return self.r
    
    def parse_data(self, yamlDict: dict) -> None:
        """_summary_
        Auto-generate the Speedster ResMap data structure
        from a given yaml recovered dict
        Args:
            yamlDict (dict): a dictionary containing the Speedster ResMap
                             data structure
        """
        if not "r" in yamlDict:
            raise TypeError("The parsed yamlDict must contain the \"r\" key")
        self.r = np.array( yamlDict["r"] )

# TODO : Develop a SpeedsterIntraLayerChargeMobilityGraph
# to save the generated graphs for each polygon of 
# a metal layer of the integrated circuit

# TODO : Develop a SpeedsterInterLayerChargeMobilityGraph
# to save the generated graphs for the mobility 
# of charge between successive metal layers of the
# integrated circuit


        
        
# TODO : develop an extraction engine, that 
# controls the extraction flux
# and provides textual results to console