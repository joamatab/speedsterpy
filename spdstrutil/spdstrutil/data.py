"""
data.py : provides additional 
data structures and interfaces 
that are essential for the good
interaction between the tool 
and the user

[author]    Diogo André Silvares Dias
[date]      2022-04-17
[contact]   das.dias@campus.fct.unl.pt
"""
from enum import Enum

class Unimplemented(object):
    """_summary_
    Unimplemented type raise class
    Args:
        object (Unimplemented): raise unimplementation error
    """
    def __init__(self, filepath):
        raise TypeError ("{} : Module not implemented yet".format(filepath))
    

class GdsLayerPurpose(Enum):
    """_summary_
    Enumerator for the purpose
    of a GDS layer
    Args:
    """
    DRAWING     = "drawing"
    TEXT        = "text"
    IDENTIFIER  = "identifier"
    DUMMY       = "dummy"
    GATE        = "gate"
    RESISTOR    = "resistor"
    MODEL       = "model"
    HIGH_VOLTAGE= "high voltage"
    FUSE        = "fuse"
    BLOCK       = "block"
    TERMINAL1   = "terminal1"
    TERMINAL2   = "terminal2"
    TERMINAL3   = "terminal3"
    BOUNDARY    = "boundary"
    LABEL       = "label"
    NET         = "net"
    PIN         = "pin"
    CUT         = "cut"
    PROBE       = "probe"
    SHORT       = "short"
    MASK        = "mask"
    MASK_ADD    = "mask add"
    MASK_DROP   = "mask drop"
    WAFFLE_DROP = "waffle drop"
    
class GdsTable(dict):
    """_summary_
    Standard GDSII table data structure dictionary
    representation, using the (layer number, datatype)
    as keys and the layer name, layer purpose and description
    as values
    """
    __slots__ = [
        "table"
    ]
    def __init__(self):
        self.table = {}
    
    def __dict__(self) -> dict:
        """_summary_
        Return the GDSTable data structure as a dict
        """
        ret = {}
        for key, value in self.table.items():
            ret[key] = {
                "name": value["name"],
                "purpose": [pur.name for pur in value["purpose"]],
                "description": value["description"]
            }
        return ret

    def __str__(self) -> str:
        """_summary_
        Return the GDSTable data structure as a string
        """
        ret  = "-----------------\n"
        ret += "GDSII Table\n"
        for key, value in self.table.items():
            ret += "-----------------\n"
            ret += "Layer: {}\n".format(key)
            ret += "Name: {}\n".format(value["name"])
            ret += "Purpose: {}\n".format([val.name for val in value["purpose"]])
            ret += "Description: {}\n".format(value["description"])
        ret += "-----------------"
        return ret
    
    def __getitem__(self, key: tuple) -> object:
        return self.table[key]

    def __setitem__(self, key: tuple, value: dict) -> None:
        self.table[key] = value
    
    def __delitem__(self, key: tuple) -> None:
        del self.table[key]
    
    def __contains__(self, key: tuple) -> bool:
        return key in self.table.keys()

    def __iter__(self) -> iter:
        return iter(self.table.key())
    
    def items(self) -> list:
        return self.table.items()
    
    def keys(self) -> list:
        return list(self.table.keys())
    
    def values(self) -> list:
        return list(self.table.values())
    
    def purposes(self) -> list:
        return list(self.table.values()["purpose"])
    
    def names(self) -> list:
        return list(self.table.values()["name"])
    
    def descriptions(self) -> list:
        return list(self.table.values()["description"])
    
    def add(
        self,
        layer: int,
        dataType: int,
        name: str,
        purpose: list,
        description: str,
    ):
        self.table[(layer, dataType)] = {
            "name": name,
            "purpose": [GdsLayerPurpose[pur] for pur in purpose],
            "description": description
        }
    
    def parseData(self, yamlDict: dict) -> None:
        """_summary_
        Auto-generate the GDSTable data structure
        from a given yaml recovered dict
        Args:
            yamlDict (dict): a dictionary containing the GDSTable
                             data structure
        """
        for key, value in yamlDict.items():
            if not "name" in value.keys():
                raise TypeError("The parsed yamlDict must contain the \"name\" key")
            if not "purpose" in value.keys():
                raise TypeError("The parsed yamlDict must contain the \"purpose\" key")
            if not "description" in value.keys():
                raise TypeError("The parsed yamlDict must contain the \"description\" key")
            self.add(
                key[0],
                key[1],
                value["name"],
                value["purpose"],
                value["description"]
            )
            
    def getLayerName(self, layer: int, dataType: int) -> str:
        """_summary_
        Return the layer name associated to the given layer number
        and data type
        Args:
            layer (int): the layer number
            dataType (int): the data type
        """
        return self.table[(layer, dataType)]["name"]
    
    def getLayerPurpose(self, layer: int, dataType: int) -> list:
        """_summary_
        Return the layer purpose associated to the given layer number
        and data type
        Args:
            layer (int): the layer number
            dataType (int): the data type
        """
        return self.table[(layer, dataType)]["purpose"]

    