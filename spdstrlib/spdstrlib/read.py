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
    #logger.info("Loading workspace library...")
    if not os.path.exists(filepath):
        raise FileNotFoundError("The workspace library \"{}\" does not exist".format(filepath))
    with open(filepath, "rb") as f:
        lib = pickle.load(f)
    dirpath, filename = os.path.split(filepath)
    #logger.info("Success loading workspace library")
    return lib

def read(workspacePath) -> SpdstrWorkspace:
    """_summary_
    Reads a saved workspace (saved in .json format)
    Args:
        workspacePath   (str)   : path of the workspace to read
    """
    if workspacePath == "":
        raise ValueError("No workspace path was specified")
    #path = os.path.abspath(workspacePath)
    path = workspacePath
    logger.info("Reading workspace from \"{}\"".format(path))
    workspace = None # returning object
    if not os.path.exists(workspacePath):
        raise FileNotFoundError("The workspace path \"{}\" does not exist".format(path))
    
    workspaceDict = {} # dictionary to save the read info
    try:
        with open(path, "r") as f:
            try:
                workspaceDict = json.load(f)
            except json.decoder.JSONDecodeError as e:
                raise json.decoder.JSONDecodeError("The workspace \"{}\" is not a valid JSON file".format(path))
    except FileNotFoundError:
        raise FileNotFoundError("The workspace path \"{}\" does not exist".format(path))
    
    if workspaceDict == {}:
        raise ValueError("The workspace \"{}\" is empty".format(path))
    try:
        workspace = SpdstrWorkspace(selfDict = workspaceDict)
    except Exception as e:
        raise e
    
    logger.info("Success reading workspace from \"{}\"".format(path))
    return workspace