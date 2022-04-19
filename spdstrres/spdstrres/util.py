from enum import Enum
import os
from argparse import Namespace
from spdstrlib import (
    __workspace_lib_path__,
    __workspace_filename__,
    read,
    load,
    SpdstrWorkspaceLib,
    SpdstrWorkspace,
)
def handleMutuallyExclusive(argv: Namespace) -> None:
    """_summary_
    handler for the mutually exclusive options
    of the command line
    Args:
        namespace (Namespace):  namespace object
                                holding the parsed arguments
                                from console, using
                                argparse subparser
    """
    if not argv.ws:
        raise ValueError("Workspace name must be provided.")
    if not( argv.ptp and argv.v ):
        raise ValueError("Visualization is only possible to occur after performing point-to-point resistance extraction (PTP).")

def handleResistanceExtraction(argv : Namespace) -> None:
    """_summary_
    Handler for the extraction of parasitic resistace
    extraction
    Args:
        argv (Namespace): _description_
    """
    ptp = False
    vis = False
    out = False
    bench = False
    workspaceName = ""
    netlistName = ""
    spefName = ""
    
    # store true arguments
    if argv.ptp:
        ptp = True
    if argv.v :
        vis = True
    if argv.o:
        out = True
    if argv.b:
        bench = True
    
    # string arguments
    if not argv.ws:
        raise ValueError("Workspace name is required.")
    workspaceName = argv.ws[0]
    
    if argv.net:
        netlistName = argv.net[0]
        
    if argv.spef:
        spefName = argv.spef[0]
    
    libPath = os.path.join(__workspace_lib_path__, __workspace_filename__)
    # load workspace library
    lib = load(libPath)
    # from workspace library, load workspace
    workspaceJsonPath = lib[workspaceName]["fullpath"]
    workspace = read(workspaceJsonPath)
    # parse the workspace to resistance extraction brigding function, along with the remaining options
    