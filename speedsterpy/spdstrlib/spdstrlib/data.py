import os
class SpdstrWorkspace(object):
    """_summary_
    A Speedster Project library object,
    to represent a user workspace
    """
    def __parse(self, dict):
        """_summary_
        Constructs a SpdstrProject object from a dictionary
        obtained from a .json file
        Args:
            dict (dict): dictionary representation of the project object
        """
        self.name = dict["name"]
        self.workspacePath = dict["workspacePath"]
        self.techPath = dict["techPath"]
        self.layoutPath = dict["layoutPath"]
        self.netlistPath = dict["netlistPath"]
        self.portsPath = dict["portsPath"]
        self.testbenchPath = dict["testbenchPath"]
        self.testbenchOutputPath = dict["testbenchOutputPath"]
        self.testbenchConfigPath = dict["testbenchConfigPath"]
    
    def __init__(self, name: str = "", workspacePath: str = "", selfDict: dict = None):
        """_summary_
        A class constructor supporting parsing capabilities
        Args:
            name            (str)               : workspace name
            workspacePath   (str, optional)     : workspace directory path. Defaults to "".
            selfDict        (_type_, optional)  : dictionary representation of the workspace, 
                                                obtained from json. Defaults to None.
        Raises:
            ValueError: 
        """
        if selfDict: # if there is a specified parsing dictionary
            self.__parse(selfDict) # construct from it
        else: # else, proceed with default constructor
            if name == "":
                raise ValueError("A project must have a name")
            self.name = name
            self.workspacePath = workspacePath            
            self.techPath = ""
            self.portsPath = ""
            self.layoutPath = ""
            self.netlistPath = ""
            self.testbenchPath = ""
            self.testbenchOutputPath = ""
            self.testbenchConfigPath = ""
    
    
    
    def __str__(self):
        ret = "--------------------------------\n"
        ret += "Workspace Name              : {}\n".format(self.name)
        ret += "Parent Directory Path       : {}\n".format(self.workspacePath)
        ret += "Technology File Path        : {}\n".format(self.techPath)
        ret += "Layout File Path            : {}\n".format(self.layoutPath)
        ret += "Circuit Netlist File Path   : {}\n".format(self.netlistPath)
        ret += "Ports File Path             : {}\n".format(self.portsPath)
        ret += "Testbench File Path         : {}\n".format(self.testbenchPath)
        ret += "Testbench Output Path       : {}\n".format(self.testbenchOutputPath)
        ret += "Testbench Configuration File: {}\n".format(self.testbenchConfigPath)
        ret += "--------------------------------\n"
        return ret

    def __repr__(self):
        return self.__str__()
    
    def __dict__(self):
        """_summary_
        Return a dictionary representation of the project object
        Returns:
            (dict) : dictionary representation of the project object
        """
        return {
            "name": self.name,
            "workspacePath": self.workspacePath,
            "techPath": self.techPath,
            "layoutPath": self.layoutPath,
            "netlistPath": self.netlistPath,
            "portsPath": self.portsPath,
            "testbenchPath": self.testbenchPath,
            "testbenchOutputPath": self.testbenchOutputPath,
            "testbenchConfigPath": self.testbenchConfigPath
        }
        
    def __iter__(self):
        return iter(self.__dict__())
    
    def saveWorkspaceDir(self, workspacePath):
        self.workspacePath = workspacePath
    
    def saveTechFile(self, techPath):
        #check file extension to see if it matches the accepted file extension
        _, tail = os.path.split(techPath)
        filename, extension = os.path.splitext(tail)
        if extension != ".tlef" and extension != ".lef":
            raise ValueError("The {} file's extension must be .tlef or .lef".format(filename))
        self.techPath = techPath
    
    def saveLayoutFile(self, layoutPath):
        _, tail = os.path.split(layoutPath)
        filename, extension = os.path.splitext(tail)
        if extension != ".gds": #or extension != ".oasis": NOT IMPLEMENTED YET!
            raise ValueError("The {} file's extension must be .gds".format(filename))
        self.layoutPath = layoutPath
    
    def saveNetlistFile(self, netlistPath):
        _, tail = os.path.split(netlistPath)
        filename, extension = os.path.splitext(tail)
        if extension != ".net" and extension != ".cir":
            raise ValueError("The {} file's extension must be .net or .cir".format(filename))
        self.netlistPath = netlistPath
    
    def savePortsFile(self, portsPath):
        _, tail = os.path.split(portsPath)
        filename, extension = os.path.splitext(tail)
        if extension != ".lef":
            raise ValueError("The {} file's extension must be .lef".format(filename))
        self.portsPath = portsPath
    
    def saveTestbenchDir(self, testbenchPath):
        self.testbenchPath = testbenchPath
        
    def saveTestbenchOutput(self, testbenchOutputPath):
        self.testbenchOutputPath = testbenchOutputPath
    
    def saveTestbenchConfig(self, testbenchConfigPath):
        self.testbenchConfigPath = testbenchConfigPath
    
    def createTestbench(self):
        """_summary_
        Creates a testbench folder for the project
        if none exists yet
        Raises:
            FileExistsError: existing file path
            FileExistsError: existing directory
            e: other unknown exceptions
        """
        if self.testbenchPath != "":
            raise FileExistsError("A testbench file already exists")
        dirname = "testbench"
        parentDir = self.workspacePath
        # create a new directory
        path = os.path.join(parentDir, dirname)
        try:
            os.makedirs(path)
        except FileExistsError:
            raise FileExistsError("A testbench directory already exists")
        except Exception as e:
            raise e
        self.saveTestbenchDir( path )
    
    def createTestbenchCfgFile(self):
        """_summary_
        Creates a testbench configuration file
        if no file exists yet
        Raises:
            FileExistsError: existing file
        """
        if "cfg.toml" in os.listdir(self.testbenchPath):
            raise FileExistsError("A testbench configuration file already exists")
        filepath = os.path.join(self.testbenchPath, "cfg.toml")
        with open(filepath, 'w') as f:
            f.write("[speedster.testbench]\n")
            f.write("workspace = \"{}\"\n".format(self.name))
            f.write("description = \"Testbench configuration file for extraction\"\n")
            f.write("testbench = \"{}\"\n".format(self.testbenchPath))
            f.write("output = \"{}\"\n".format(self.testbenchOutputPath))
        self.saveTestbenchConfig( filepath )

    # TODO : def parseTestbenchConfig(self, **kwargs):
    # Create the parser for the automatic configuration of the testbench config file
    def parseTestbenchConfig(self, **kwargs):
        """_summary_
        Parser for the automatic configuration
        of the testbench config file
        """
        pass

    def createTestbenchOutputDir(self):
        """_summary_
        Creates a testbench extraction output
        folder for the project if none exists yet
        Raises:
            FileExistsError: existing file path
            FileExistsError: existing directory
        """
        if self.testbenchOutputPath != "":
            raise FileExistsError("A testbench output directory already exists")
        dirname = "output"
        parentDir = self.testbenchPath
        # create a new directory
        path = os.path.join(parentDir, dirname)
        try:
            os.mkdir(path)
        except FileExistsError:
            raise FileExistsError("A testbench output directory already exists")
        self.saveTestbenchOutput( path )
class SpdstrWorkspaceLib(object):
    """_summary_
    A workspace library is a dictionary of workspace name : paths
    This object is to be saved as binary file (.bin) after each workspace is added
    Args:
        object (_type_): _description_

    Raises:
        FileNotFoundError: _description_
        FileNotFoundError: _description_

    Returns:
        _type_: _description_
    """
    __slots__ = [
        "libPath",
        "libFileName",
        "lib", 
    ]
    
    def __parse(self, lib):
        for key, value in lib.items():
            self.lib[key] = value
    
    
    def __init__(   
            self, 
            libPath: str = "",
            fileName: str = "",
            lib: dict = None
        ):
        if not os.path.isdir(libPath):
            raise FileNotFoundError("The workspace library path \"{}\" is not a directory".format(libPath))
        self.libPath = libPath
        self.libFileName = fileName
        self.lib = {}
        if lib:
            self.__parse(lib)
    
    def __str__(self):
        ret  = "--------------------------------\n"
        ret += "Workspace Library:\n"
        ret += "--------------------------------\n"
        for key, value in self.lib.items():
            ret += "Workspace Name      :   {}\n".format(key)
            ret += "Workspace Path      :   {}\n".format(value["parent"])
            ret += "Workspace Full Path :   {}\n\n".format(value["fullpath"])
        ret += "--------------------------------\n"
        return ret
    
    def __iter__(self):
        return iter(self.lib)

    def __getitem__(self, key):
        if key not in self.lib:
            raise KeyError("The key \"{}\" does not exist".format(key))
        return self.lib[key]

    def add(self, workspace: SpdstrWorkspace, overWrite = False) -> None:
        if not overWrite:
            if workspace.name in self.lib.keys():
                raise KeyError("The workspace name \"{}\" already exists".format(workspace.name))
        fullpath = os.path.join(workspace.workspacePath, "{}.json".format(workspace.name))
        self.lib[workspace.name] = {"parent":workspace.workspacePath,"fullpath": fullpath}
        
    def remove(self, workspaceName: str) -> None:
        if workspaceName not in self.lib.keys():
            raise KeyError("The workspace name \"{}\" does not exist".format(workspaceName))    
        del self.lib[workspaceName]
    
    def defineWorkspaceLibPath(self, workspaceLibPath: str) -> None:
        if not os.path.isdir(workspaceLibPath):
            raise FileNotFoundError("The workspace library path \"{}\" is not a directory".format(workspaceLibPath))
        self.libPath = workspaceLibPath

    def getWorkspaceLibPath(self) -> str:
        return os.path.join(self.libPath, self.libFileName)

    def clearWorkspaceLib(self) -> None:
        self.lib.clear()
        