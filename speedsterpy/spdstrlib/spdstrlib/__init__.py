__version__ = '0.1.0'
__description__ = "Speedster project library management tool."
__date__ = "2022-04-12"
__author__ = "Diogo André Silvares Dias"
__annotations__ = ""

import argparse
import sys
from loguru import logger
import pickle
from .data import *

from .read import(
    load,
    read,
)
from .write import(
    dump,
    write
)

def getParent(path, levels = 1):
    common = path
    for i in range(levels+1):
        common = os.path.dirname(os.path.abspath(common))
    return common
#create the global workspace lib path save
file = os.path.abspath(__file__)
parent = getParent(file, 1)
__workspace_lib_path__ = "{}/resources".format(parent)
if not os.path.exists(__workspace_lib_path__):
    os.makedirs(__workspace_lib_path__)
__workspace_filename__ = "wslib.bin"


def verboseInfo():
    print("Version      : {} ({})".format(__version__, __date__))
    print("Authors      : {}".format(__author__))
    print("Description  : {}".format(__description__))

def run(subparser, *args, **kwargs) -> None:
    logger.info("Speedster$\nLibrary Manager : {}".format(__file__))
    try:
        argv = subparser.parse_args(sys.argv[2:])
    except Exception as e:
        logger.error(e)
    if argv.info:
        verboseInfo()
    # TODO : implment the interaction of the user with the library    