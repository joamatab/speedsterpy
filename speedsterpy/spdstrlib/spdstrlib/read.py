import os
import sys
from loguru import logger
import pickle
import json
from .data import *

def load(libPath = "") -> SpdstrWorkspaceLib:
    """
    Read the workspace library (saved in .bin (binary) format)
    Args:
        libPath (str): if can either be a dir path (foo/bar)
                        or a binary file path (foo/bar/baz.bin)
    """
    filepath = ""
    if libPath != "":
        head, tail = os.path.split(libPath)
        name, extension = os.path.splitext(tail)
        if extension != ".bin":
            raise ValueError("The workspace library path \"{}\" is not a .bin file".format(libPath))
        filepath = libPath
    logger.info("Loading workspace library...")
    if not os.path.exists(filepath):
        raise FileNotFoundError("The workspace library \"{}\" does not exist".format(filepath))
    with open(filepath, "rb") as f:
        lib = pickle.load(f)
    dirpath, filename = os.path.split(filepath)
    logger.info("Success loading workspace library")
    return lib

def read(workspacePath) -> SpdstrWorkspace:
    """_summary_
    Reads a saved workspace (saved in .json format)
    Args:
        workspacePath   (str)   : path of the workspace to read
    """
    logger.info("Reading workspace from \"{}\"".format(workspacePath))
    workspace = None # returning object
    if workspacePath == "":
        raise ValueError("No workspace path was specified")
    
    if not os.path.exists(workspacePath):
        raise FileNotFoundError("The workspace path \"{}\" does not exist".format(workspacePath))
    
    workspaceDict = {} # dictionary to save the read info
    with open(workspacePath, "r") as f:
        try:
            workspaceDict = json.load(f)
        except json.decoder.JSONDecodeError as e:
            raise json.decoder.JSONDecodeError("The workspace \"{}\" is not a valid JSON file".format(workspacePath))
    
    if workspaceDict == {}:
        raise ValueError("The workspace \"{}\" is empty".format(workspacePath))

    try:
        workspace = SpdstrWorkspace(selfDict = workspaceDict)
    except TypeError as e:
        raise e

    logger.info("Success reading workspace from \"{}\"".format(workspacePath))
    return workspace