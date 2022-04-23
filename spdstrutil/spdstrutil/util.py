"""
util.py : provides aditional utilities
that come in handy during the development
"""
from collections import defaultdict
from functools import wraps # wrap function parse inputs from subparser arguments 
from .data import (
    GdsTable,
    GdsLayerPurpose,
)

def getGdsTableEntriesFromPurpose(other: GdsTable, purpose: GdsLayerPurpose) -> GdsTable:
    """_summary_
    Get a new GdsTable object from a GdsTable object
    by selecting only the rows with the specified purpose
    Args:
        other   (GdsTable)          : GdsTable object to be filtered
        purpose (GdsLayerPurpose)   : purpose to be aapplied as filter
    Returns:
        GdsTable: filtered GdsTable object
    """
    newTab = GdsTable()
    for key, value in other.items():
        if purpose in value["purpose"]:
            newTab.table[key] = value
    return newTab

def getGdsTableEntriesFromLayerName(other: GdsTable, layerName: str) -> GdsTable:
    """_summary_
    Get a new GdsTable object from a GdsTable object
    by selecting only the rows with the specified layer name
    Args:
        other   (GdsTable)          : GdsTable object to be filtered
        layerName (str)             : layer name to be aapplied as filter
    Returns:
        GdsTable: filtered GdsTable object
    """
    newTab = GdsTable()
    for key, value in other.items():
        if layerName in value["name"]:
            newTab.table[key] = value
    return newTab

def getGdsLayerDatatypeFromLayerNamePurpose(other : GdsTable, layerName: str, purpose: GdsLayerPurpose) -> tuple:
    """_summary_
    Get the datatype of a layer from a GdsTable object
    by selecting only the rows with the specified layer name and purpose
    Args:
        other       (GdsTable)  : GdsTable object to be filtered
        layerName   (str)       : layer name to be aapplied as filter
        purpose     (str)       : purpose to be aapplied as filter
    Returns:
        tuple: datatype of the layer
    """
    for key, value in other.items():
        if layerName == value["name"] and purpose in value["purpose"]:
            return key
    return None
    
def getDrawingMetalLayersMap(table: GdsTable, maxMetalNum = 15) -> dict:
    """_summary_
    Get a dictionary with the metal layers used for drawing
    metal shapes and interconnects in the imported gds table.
    Args:
        table       (GdsTable)      : GDS table associated with a given tech node.
        maxMetalNum (int, optional) : Maximum number of routing metal layers. Defaults to 15.
    Returns:
        dict: "layer name" : (layer, datatype) map
    """
    # get the ordered metal layers and 
    via = "via"
    met = "met"
    layerMap = {}
    # don't use the first layer, since it is a via layer
    #layerMap["mcon"] = getGdsLayerDatatypeFromLayerNamePurpose("mcon", GdsLayerPurpose.DRAWING)
    layerMap["met1"] = getGdsLayerDatatypeFromLayerNamePurpose(table,"met1", GdsLayerPurpose.DRAWING)
    layerMap["via"] = getGdsLayerDatatypeFromLayerNamePurpose(table, "via", GdsLayerPurpose.DRAWING)
    for i in range(2,maxMetalNum):#maximum number of metal layers 
        aux = getGdsLayerDatatypeFromLayerNamePurpose(table,"{}{}".format(met,str(i)), GdsLayerPurpose.DRAWING)
        if aux != None:
            layerMap["{}{}".format(met,str(i))] = aux
            lastVia = i
        else: # if the routing metal layer is not found, stop
            break
        aux = getGdsLayerDatatypeFromLayerNamePurpose(table,"{}{}".format(via,str(i)), GdsLayerPurpose.DRAWING)
        if aux != None:
            layerMap["{}{}".format(via,str(i))] = aux
            lastMetal = i
    return layerMap

def addBackannotation(table: GdsTable) -> GdsTable:
    """_summary_
    Add dedicated drawing layers for performing backannotation
    on the layout
    Args:
        table (GdsTable): the imported table to which the items will be added
    Returns:
        GdsTable: the same library as the one received, but with the added items
    """
    # back annotation will only be performed on metal layers or vias layers
    metalLayerNames = list(getDrawingMetalLayersMap(table).keys())
    forbiddenLayerDatatypes = defaultdict(list) # list of forbidden (layer, datatype) tuples
    possibleLayerDatatypes = {} # list of possible (layer, datatype) tuples
    for name in metalLayerNames:
        for key in list(getGdsTableEntriesFromLayerName(table, name).keys()):
            if key not in forbiddenLayerDatatypes[name]:
                forbiddenLayerDatatypes[name].append(key)
        for key in forbiddenLayerDatatypes[name]:
            if (key[0], key[1]+1) not in forbiddenLayerDatatypes[name]:
                possibleLayerDatatypes[name] = (key[0], key[1]+1)
    for name, key in possibleLayerDatatypes.items():
        table.add(key[0], key[1], name, [GdsLayerPurpose.BACKANNOTATION.name], "{} backannotation".format(name))
    return table