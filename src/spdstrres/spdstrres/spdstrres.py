import sys
from loguru import logger
from __init__ import(
    __version__,
    __author__,
    __date__,
    __description__
)

def getInfo():
    print("Version      : {} ({})".format(__version__, __date__))
    print("Authors      : {}".format(__author__))
    print("Description  : {}".format(__description__))

def run(subparser, *args, **kwargs) -> None:
    logger.info("Speedster$\nResistance PEX : {}".format(__file__))
    argv = subparser.parse_args(sys.argv[2:])
    getInfo()
    print("Received args: {}".format(args))
    print("Received namespace: {}".format(argv))
    raise NotImplementedError("{} : Not implemented yet {}".format(sys._getframe(),sys._getframe().f_code.co_name))