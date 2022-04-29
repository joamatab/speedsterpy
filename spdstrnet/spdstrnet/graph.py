"""_summary_
graph.py contains the main functionalities 
for the creation and manipulation of place and trasition
graphs representing the mobility of charge within the IC layout 

[author]    Diogo André Silvares Dias
[date]      2022-04-17
[contact]   das.dias@campus.fct.unl.pt
"""
from enum import Enum
from gdspy import (
    GdsCell,
    PolygonSet,
    Polygon,
    Rectangle,
)
from .data import (
    SpeedsterPort,
)
from networkx import (
    DiGraph,  # directed graph
)


def _map_fragments_current_path(
    fragments: PolygonSet,
    startingPort: SpeedsterPort,
    endingPort: SpeedsterPort = None,
) -> DiGraph:
    """_summary_
    Create a graph mapping the path of current
    throught each fragment of the layout, starting from a
    given port, and optionally ending at another port
    """
    pass


def _map_net_connections(
    layout: GdsCell,
    startingPort: SpeedsterPort,
    endingPort: SpeedsterPort = None,
) -> DiGraph:
    """_summary_
    Create a graph mapping the path of current
    throught the layers of the layout (passing through each via)
    from a starting port until an optional ending port.
    """
    pass


# todo: develop the algorithm to
# follow the electric current path through out the nodes
# of the layout, computing the graph of the charge mobility
# for each received gdspy polygon / path received as input
