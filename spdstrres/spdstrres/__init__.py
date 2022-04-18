__version__ = '0.1.2'
__description__ = "Speedster point-to-point parasitic resistance extraction tool."
__date__ = "2022-12-21"
__author__ = "Diogo André Silvares Dias"
__annotations__ = ""

import sys
from loguru import logger
from spdstrres import *
import argparse

def verboseInfo():
    print("Version      : {} ({})".format(__version__, __date__))
    print("Authors      : {}".format(__author__))
    print("Description  : {}".format(__description__))

def run(subparser, *args, **kwargs) -> None:
    logger.info("Speedster$\nResistance PEX : {}".format(__file__))
    argv = subparser.parse_args(sys.argv[2:])
    if argv.info:
        verboseInfo()
        return None
    # handle the mutually exclusive options
    