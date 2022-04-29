"""_summary_
rpex.py aggregates the main functionalities
of the path.py, graph.py and res.py modules, 
establishing a framework for the interaction of
the user with the resistance extraction engine 

[author]    Diogo André Silvares Dias
[date]      2022-04-17
[contact]   das.dias@campus.fct.unl.pt
"""

from loguru import logger
import sys

sys.path.append("../spdstrutil")
from spdstrutil import (
    Unimplemented,
)
from spdstrlib import (
    SpdstrWorkspace,
)


def runResPex(
    workspace: SpdstrWorkspace,
    ptp=False,
    vis=False,
    out=False,
    bench=False,
    netlistName="",
    spefName="",
) -> Unimplemented:
    return Unimplemented("spdstrres/rpex/runResPex")
