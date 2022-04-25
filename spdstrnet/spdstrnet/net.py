import itertools
from loguru import logger
from enum import Enum
import numpy as np
from gdstk import(
    GdsLibrary,
    Cell,
    PolygonSet,
    Path,
    Text,  # to provide a text annotation system
    Label, # to provide label knowledge
    # functions
    boolean, # perform boolean operations on two polygon sets
    inside, # check if a point is inside a polygon
    copy, # create and return a copy of a polygon set
)
from .geometry import(
    bool_polygon_overlap_check,
    check_polygon_in_cell,
    check_polygon_overlap,
    check_same_polygon,
    join_overlapping_polygons_cell,
    get_polygon_dict,
    check_polygon_contains_polygon,
    fuse_overlapping_cells,
)
from .data import(
    SpeedsterPort,
)
from spdstrutil import (
    GdsTable,
    GdsLayerPurpose,
    timer,
)

def _recursive_net_search(
    previousViasPolygon,
    polyDict,
    layerIndex,
    net,
):
    """_summary_
    (Descending order of metal layers)
    Recursively searches for the polygons of the metal alyer above
    that intercept the vias polygons parsed as input
    Args:
        previousViasPolygon (PolygonSet): vias polygons of the layer below
        polyDict            (dict)      : dictionary of {(layer, datatype): [polygons]} tuples
        layerIndex          (int)       : polyDict keys list index of the current vias polygons (layer, datatype) tuple        
        net                 (gdspy.Cell): gdspy.Cell object containing the net that is being extracted 

    Returns:
    
    """
    layerDatatypeList = list(polyDict.keys())
    if layerIndex >= len(layerDatatypeList):
        return # reached the highest layer, the search is over
    layer,datatype = layerDatatypeList[layerIndex]
    # for each polygon of the m2 layer
    #poly_id = 0
    for polyset in list(polyDict[(layer, datatype)]):
        #print(f'Poly Layer : {lindex} Poly id : {poly_id}')
        # if the m2m1 vias polys that intersept the M1 layer intersept the m2 layer as well, add the poly to the netlist
        if bool_polygon_overlap_check(polyset, previousViasPolygon):
            if not check_polygon_in_cell(polyset, net):
                net.add(polyset)
            # check then the m3_m2 vias that intersect the same m2 layer, and add them to the netlist
            auxLayerIndex = layerIndex + 1
            if auxLayerIndex < len(layerDatatypeList):
                viaLayer, viaDatatype = layerDatatypeList[auxLayerIndex]
                # get intercepting vias above the current layer
                if bool_polygon_overlap_check(polyset, polyDict[(viaLayer,viaDatatype)]): # if there are intersepting vias
                    nextViasPolygons = check_polygon_overlap(polyset, polyDict[(viaLayer,viaDatatype)], viaLayer, viaDatatype)
                    if not check_polygon_in_cell(polyset, net):
                        net.add(nextViasPolygons) # add the vias polygons to the netlist
                    _recursive_net_search(nextViasPolygons, polyDict, auxLayerIndex+1, net)

def _reverse_recursive_net_search(
    previousViasPolygon,
    polyDict,
    layerIndex,
    net,
) :
    """_summary_
    (Descending order of metal layers)
    Recursively searches for the polygons of the metal layer below
    that intercept the vias polygons parsed as input 
    Args:
        previousViasPolygon (PolygonSet): vias polygons of the layer above
        polyDict            (dict)      : dictionary of {(layer, datatype): [polygons]} tuples
        layerIndex          (int)       : polyDict keys list index of the current vias polygons (layer, datatype) tuple        
        net                 (gdspy.Cell): gdspy.Cell object containing the net that is being extracted 

    Returns:
    
    """
    layerDatatypeList = list(polyDict.keys())
    if layerIndex < 0:
        return # reached the lowest layer i nthe previous iteration, the search is over
    layer,datatype = layerDatatypeList[layerIndex]
    # for each polygon of the m2 layer
    #poly_id = 0
    for polyset in list(polyDict[(layer, datatype)]):
        #print(f'Poly Layer : {lindex} Poly id : {poly_id}')
        # if the m2m1 vias polys that intersept the M1 layer intersept the m2 layer as well, add the poly to the netlist
        if bool_polygon_overlap_check(polyset, previousViasPolygon):
            if not check_polygon_in_cell(polyset, net):
                net.add(polyset)
            # check then the m3_m2 vias that intersect the same m2 layer, and add them to the netlist
            auxLayerIndex = layerIndex - 1
            if auxLayerIndex >= 0:
                viaLayer, viaDatatype = layerDatatypeList[auxLayerIndex]
                # get intercepting vias above the current layer
                if bool_polygon_overlap_check(polyset, polyDict[(viaLayer,viaDatatype)]): # if there are intersepting vias
                    nextViasPolygons = check_polygon_overlap(polyset, polyDict[(viaLayer,viaDatatype)], viaLayer, viaDatatype)
                    if not check_polygon_in_cell(polyset, nextViasPolygons):
                        net.add(nextViasPolygons) # add the vias polygons to the netlist
                    _recursive_net_search(nextViasPolygons, polyDict, auxLayerIndex-1, net)


def _net_connection_search(
    polygonLayerIndex: int, # layer where the current polygon is situated in
    viaIndex: int,          # vias through which the connection happens
    metalLayerIndex: int,   # layer where the search for connections is performed
    currentPolygon,         # current polygon from which the connection is beggining in
    polyDict: dict,
    net: Cell,
):
    """_summary_
    Recursively searches for the polygons of different metal layers that
    are connected between each other through at least a single via
    Args:
        polygonLayerIndex (int)         : index of the layer where the current polygon is situated
        viaIndex          (int)         : index of the vias layer through which the connection happens
        metalLayerIndex   (int)         : index of the metal layer where the search for connections is performed
        currentPolygon    (PolygonSet)  : current polygon from which the connection is beggining in
        polyDict          (dict)        : dictionary of {(layer, datatype): [polygons]} tuples
        net               (Cell)        : gdspy.Cell object containing the net that is being extracted
    """
    metalLayers = list(polyDict.keys())
    # end of search conditions
    if viaIndex < 0 or viaIndex > len(metalLayers):
        return
    if metalLayerIndex < 0 or metalLayerIndex > len(metalLayers):
        return
    if polygonLayerIndex < 0 or polygonLayerIndex > len(metalLayers):
        return
    # otherwise, continue the search
    viaLayer, viaDatatype = metalLayers[viaIndex][0], metalLayers[viaIndex][1]
    vias = check_polygon_overlap(currentPolygon, polyDict[metalLayers[viaIndex]], viaLayer, viaDatatype)
    if not check_polygon_in_cell(vias, net):
        vias.properties['net'] = net.name
        net.add(vias)
    for poly in polyDict[metalLayers[metalLayerIndex]]:
        if bool_polygon_overlap_check(poly, vias):
            if not check_polygon_in_cell(poly, net):
                poly.properties['net'] = net.name
                net.add(poly)
            _net_connection_search(metalLayerIndex, viaIndex+2, metalLayerIndex+2, poly, polyDict, net)
            _net_connection_search(metalLayerIndex, viaIndex-2, metalLayerIndex-2, poly, polyDict, net)

@timer
def _total_unlabeled_net_extract(
    layout: Cell,
    gdsTable: GdsTable,
) -> GdsLibrary:
    """_summary_
    Extracts all the metal nets from a layout Cell object by performing
    multiple polygon boolean operations,
    returning a GdsLibrary with the extracted nets
    Args:
        layout      (Cell)          : Cell object containing the layout
        nets        (GdsLibrary)    : GdsLibrary object to which the extracted nets will be added
        gdsTable    (GdsTable)      : GdsTable object containing the gds information
    Returns:
        GdsLibrary : GdsLibrary object containing the extracted nets
    """
    logger.info("Extracting metal nets through geometry processing...")
    netId = 0
    nets = [] # temporary list to save the generated Cell nets
    # layerMap starts in met1 layer, followed by a via, met, via ....
    layerMap = gdsTable.getDrawingMetalLayersMap()
    # the number of metal layers selected for extraction 
    # is either 1, 3, 5, 7 or 9
    startingLayerIndex = startingLayerIndex = round(len(polyDict.keys())/2.0)-1 if len(polyDict.keys()) > 3 else 0
    # obtain a layout of adjoint polygons
    unitedCell = join_overlapping_polygons_cell(layout, layerMap)
    polyDict = get_polygon_dict(unitedCell,specs=layerMap.values())
    #each of the polygons of the central routing metal layer will be a starting polygon
    # for the search
    for poly in polyDict[ list(polyDict.keys())[startingLayerIndex] ]:
        # create a new net
        newNet = Cell(f'net_{netId}', exclude_from_current=True)
        # add the starting polygon to the net
        poly.properties['net'] = newNet.name
        newNet.add(poly)
        # search for the rest of the polygons that are connected to the starting polygon
        _net_connection_search(
            startingLayerIndex, 
            startingLayerIndex+1, 
            startingLayerIndex+2, 
            poly, 
            polyDict,
            newNet
        )
        _net_connection_search(
            startingLayerIndex, 
            startingLayerIndex-1, 
            startingLayerIndex-2, 
            poly, 
            polyDict,
            newNet
        )
        # add the net to the list of nets
        nets.append(newNet)
    
    # create a GdsLibrary object to store the extracted nets
    netsLib = GdsLibrary("nets")
    # Join the nets that have at least one polygon in common, creating a new net
    # !TROUBLE IN THIS SNIPPET ************
    def mapFunc(netA, netB):
        if netA.name != netB.name:
            fusion = fuse_overlapping_cells(netA, netB)
            if fusion is not None:
                return fusion
    # run the fusion process until the number of fused nets together doesn't change anymore
    fusedNets = nets
    length = len(fusedNets)
    prevLength = 0
    while length != prevLength:
        fusedNets = list(map(mapFunc, nets, fusedNets))
        prevLength = length
        length = len(fusedNets)
    # ! TROUBLE IN THIS SNIPPET ***********  
    # normalize the fused nets
    def _normalize_nets(
        net: Cell  
    ) -> Cell:
        """_summary_
        """
        for poly in net.polygons:
            poly.properties['net'] = net.name
        return net
    fusedNets = [_normalize_nets(net) for net in fusedNets]
    # finally, add the fused nets to the nets gds library
    [netsLib.add(net) for net in fusedNets]
    labels = [cellName for cellName in netsLib.cells.keys()]
    logger.info("Net extraction is complete. Nets found :{}".format(len(labels)))
    logger.warning("Net renaming is advised!")
    return netsLib


@timer
def _unlabeled_net_extraction(
    entryPolygon,
    layout: Cell,
    gdsTable: GdsTable,
    netName = "net",
) -> Cell :
    """_summary_
    Performs the automatic extraction of the net
    to which the entry polygon belongs to from the layout
    without recurring to the labelling of each polygon.
    Args:
        entryPolygon (PolygonSet) : polygon from which the extraction is started
        layout       (Cell)       : Cell object containing the layout
        gdsTable     (GdsTable)   : GdsTable object containing the gds information
    Returns:
        Cell : gdspy.Cell object containing the extracted net
    """
    net = Cell(netName, exclude_from_current=True)
    entryLayer = entryPolygon.layers[0]
    entryDataType = entryPolygon.datatypes[0]
    # layerMap starts in met1 layer, followed by a via, met, via ....
    layerMap = gdsTable.getDrawingMetalLayersMap()
    if "via" in gdsTable[(entryLayer, entryDataType)]:
        raise ValueError("Entry Polygon must be a routing metal polygon! It cannot be a via!")
    
    # obtain a layout of adjoint polygons
    unitedCell = join_overlapping_polygons_cell(layout, layerMap)
    polyDict = get_polygon_dict(unitedCell,specs=layerMap.values())
    unitedCellEntryPolygon = None
    for poly in itertools.chain(unitedCell.get_polygonsets(), unitedCell.get_polygons()):
        if check_polygon_contains_polygon(poly, entryPolygon) or check_polygon_contains_polygon(entryPolygon, poly):
            unitedCellEntryPolygon = poly
            poly.properties['net'] = netName
            net.add(poly)
            break
    # starting from the entry polygon, perform a recursive search for the net
    polygonLayerIndex = list(polyDict.keys()).index((entryLayer, entryDataType))    
    _net_connection_search(
        polygonLayerIndex, 
        polygonLayerIndex+1, 
        polygonLayerIndex+2, 
        unitedCellEntryPolygon, 
        polyDict,
        net
    )
    _net_connection_search(
        polygonLayerIndex, 
        polygonLayerIndex-1, 
        polygonLayerIndex-2, 
        unitedCellEntryPolygon, 
        polyDict, 
        net
    )
    return net

def _labeled_net_extract(
    layout: Cell,
    gdsTable: GdsTable,
    netName: str = "net"
) -> Cell:
    """_summary_
    Tries to extracts a metal net from a Cell object by 
    detecting the labels of each polygon,
    returning a GdsLibrary with the extracted nets.
    If the labels mean nothing, tries to extract using 
    _extract_nets_through_intersect function
    Args:
        layout (Cell) : Cell object containing the layout
    Returns:
        GdsLibrary : GdsLibrary object containing the extracted nets
    """
    net = Cell(netName, exclude_from_current=True)
    for poly in itertools.chain(layout.get_polygonsets(), layout.get_paths()):
        if poly.properties.get("net") == netName:
            # add proceed to the reconstruction of the net
            net.add(poly)
    return net

@timer
def net_extract(
    entryPolygon,
    layout: Cell,
    nets: GdsLibrary,
    gdsTable: GdsTable,
) -> Cell :
    """_summary_
    Performs the selection between the labeled
    or unlabeled extraction of a net from the layout
    Args:
        entryPolygon (_type_): _description_
        layout (Cell): _description_
        nets (GdsLibrary): _description_
        gdsTable (GdsTable): _description_
    Returns:
        Cell: extracted net
    """
    pass
    #TODO ! implement the extraction of a net from a layout using either labeled or unlabeled extraction

def highlight_net(
    layout: Cell,
    net: Cell,
    gdsTable: GdsTable,
) -> Cell:
    """_summary_
    Highlights an extracted net by copying the polygons
    of this same net into the main layout Cell while
    placing them in the dedicated highlighting gds layer.
    Args:
        layout      (Cell)      : Cell object containing the layout
        net         (Cell)      : Cell object containing the extracted net
        gdsTable    (GdsTable)  : GdsTable object containing the gds information
    Returns:
        Cell: Created highlighted net
    """
    #get the polygons of the extracted net
    polys = net.get_polygons()
    # get the layer and datatype of the highlighting layer
    highlightLayer,highlightDatatype = gdsTable.getGdsLayerDatatypeFromLayerNamePurpose("highlight", GdsLayerPurpose.HIGHLIGHTING)[0]
    # copy the polygon into the layout
    layout.add(PolygonSet(polys, layer=highlightLayer, datatype=highlightDatatype))
    return layout

def delete_highlighted_net(
    layout: Cell,
    gdsTable: GdsTable,
) -> Cell:
    """_summary_
    Deletes the highlighting gds layer by removing
    all the polygons that were placed in it.
    Args:
        layout      (Cell)      : Cell object containing the layout
        gdsTable    (GdsTable)  : GdsTable object containing the gds information
    Returns:
        Cell: Modified layout
    """
    # get the layer and datatype of the highlighting layer
    highlightLayer,highlightDatatype = gdsTable.getGdsLayerDatatypeFromLayerNamePurpose("highlight", GdsLayerPurpose.HIGHLIGHTING)[0]
    def test(poly, l, dt):
        return l == highlightLayer and dt == highlightDatatype
    layout = layout.remove_polygons(test)
    return layout

def rename_net(
    prevNet: str,
    net: str,
    layout: Cell,
):
    """_summary_
    Renames a net by replacing the name of the net
    in the properties of each gds polygon
    Args:
        prevNet (str)   : previous net name
        net     (str)   :  new net name
        layout  (Cell)  : Cell object containing the layout
    """
    for poly in layout.get_polygonsets():
        poly.properties['net'] = net if poly.properties['net'] == prevNet else poly.properties['net']
    return layout