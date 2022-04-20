"""
util.py : provides aditional utilities
that come in handy during the development
"""
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
    
    