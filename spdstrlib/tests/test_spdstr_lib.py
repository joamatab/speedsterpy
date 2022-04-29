from loguru import logger
import os
from spdstrlib import (
    __workspace_filename__,
    __workspace_lib_path__,
    SpdstrWorkspaceLib,
    SpdstrWorkspace,
    read, 
    write, 
    dump, 
    load,
    __version__,
    getParent, 
)

def test_version():
    assert __version__ == '0.1.0'

def test_workspace_lib_creation():
    lib = SpdstrWorkspaceLib(
        libPath=__workspace_lib_path__,
        fileName=__workspace_filename__,
    )
    assert type(lib) == SpdstrWorkspaceLib
    assert lib.libPath == __workspace_lib_path__
    assert lib.libFileName == __workspace_filename__
    #save workspace library
    dump(lib)

def test_workspace_creation():
    """_summary_
    Test the creation of a workspace
    """ 
    #load library from standard path:
    path = os.path.join(__workspace_lib_path__, __workspace_filename__)
    lib = load(path)

    #parent = os.path.dirname(os.path.abspath(__file__))
    file = os.path.abspath(__file__)
    parent = getParent(file, 1)
    logger.info("\nParent directory:{}".format(parent))
    newWorkspace = SpdstrWorkspace("test_project")
    projectDir = f"{parent}/resources/temp"
    newWorkspace.saveWorkspaceDir(projectDir)
    newWorkspace.saveTechFile(f"{projectDir}/test.tlef")
    newWorkspace.saveLayoutFile(f"{projectDir}/test.gds")
    lib.add(newWorkspace)
    print(newWorkspace)
    assert type(newWorkspace) == SpdstrWorkspace
    assert newWorkspace.name == "test_project"
    assert newWorkspace.workspacePath == "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrlib/resources/temp"
    assert newWorkspace.techPath == "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrlib/resources/temp/test.tlef"
    assert newWorkspace.layoutPath == "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrlib/resources/temp/test.gds"
    logger.info("Success creating a new project:\n{}".format(str(newWorkspace)))
    #create a testbench directory
    newWorkspace.createTestbench()
    # create a testbench output child directory
    newWorkspace.createTestbenchOutputDir()
    # create a testbench configuration .toml file
    newWorkspace.createTestbenchCfgFile()

    print(newWorkspace)

    # save the workspace library
    dump(lib)
    
def test_workspace_write():
    """_summary_
    Test the writing of a workspace to json file
    """
    # load the workspace library
    path = os.path.join(__workspace_lib_path__, __workspace_filename__)
    lib = load(path)

    #parent = os.path.dirname(os.path.abspath(__file__))
    file = os.path.abspath(__file__)
    parent = getParent(file, 1)
    logger.info("\nParent directory:{}".format(parent))
    newWorkspace = SpdstrWorkspace("test_project_v2")
    projectDir = f"{parent}/resources/temp2"
    newWorkspace.saveWorkspaceDir(projectDir)
    newWorkspace.saveTechFile(f"{projectDir}/test2.tlef")
    newWorkspace.saveLayoutFile(f"{projectDir}/test2.gds")
    lib.add(newWorkspace)
    write(newWorkspace)
    print("Updated library:")
    try:
        print(lib)
    except Exception as e:
        pass

    # save the workspace library
    dump(lib)
    

def test_workspace_read():
    """_summary_
    Test the reading of a workspace from json file
    """
    # load the workspace library
    path = os.path.join(__workspace_lib_path__, __workspace_filename__)
    lib = load(path)
    wspath = lib["test_project_v2"]["fullpath"]
    newWorkspace2 = read(wspath)
    logger.info("\n{}".format(str(newWorkspace2)))
    

    
