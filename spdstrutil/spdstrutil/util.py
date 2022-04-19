"""
util.py : provides aditional utilities
that come in handy during the development
"""
from .data import (
    GdsTable,
    GdsLayerPurpose,
)

def getFromPurpose(other: GdsTable, purpose: GdsLayerPurpose) -> GdsTable:
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