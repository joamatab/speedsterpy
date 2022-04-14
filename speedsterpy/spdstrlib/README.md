# Speedster Library Manager package
Provides an interface to create and manage multiple project libraries.
Each created library will be a software representation of the workspace directory of the user's project directory. This parent directory can be composed of:
- A ```.tlef``` file with the rules of the semiconductor technology associated with the project
- A ```.gds``` file with the layout of integrated circuit
- A ```.net``` file with the (SPICE - LtSpice) circuit netlist of the integrated circuit
- A ```.lef``` file containing the port and pin locations associated with the integrated circuit
- And finally, an optional ```testbench``` child directory to which all the extraction results will saved into

The overall file tree for each project library can assimilate to:
```tree
Project Workspace (name)/
|
|--testbench/
|   |--output/ (extraction output files)
|   |
|   |--cfg.toml (extraction config file)
|   /
|
|--tech.tlef (optional)
|
|--example_ic.gds (mandatory)
|
|--example_ic.net (mandatory)
|
|--example_ic.lef (mandatory)
/
```

## Important note:

The ```.tlef``` semiconductor technology file may not be provided if the filepath to this type of file is provided.

# Usage (With Examples)
Create a new Project Library and add a newly created Workspace:
```Python
from spdstrlib.spdstrlib import *
from spdstrlib.spdstrlib import(
    __workspace_lib_path__, # default library path = "../resources/"
    __workspace_filename__ # default library name = "wslib.bin"
)
# create a new lib
newLib = SpdstrWorkspaceLib()

newProj = SpdstrWorkspace("new-project") # name the workspace: "new-project"
```

Associate new files:
```Python
# save "new-project" workspace parent directory
newProj.saveWorkspaceDir("foo/bar")

# save a new tech rule filepath
lef_file_path = "foo/bar/sky130.tlef"
newProj.saveLef(lef_file_path)

#save a new layout filepath
gds_file_path = "foo/bar/new_ic.gds"
newProj.saveGds(gds_file_path)

# add the new project to the created lib
newLib.add(newProj)

# save the library to computer memory in binary (.bin) format
dump(newLib)
```

Export the workspace directory tree to JSON:
```Python
# export to .json (default and the only supported format so far)
write(newProj)
``` 

Import the workspace to the application:
```Python
# load the library from computer memory
path = os.path.join(__workspace_lib_path__, __workspace_filename__)
importedLib = load(path)

workspace_path = "foo/bar/new-project.json"
#or get the path from the lib
workspace_path = newLib["new-project"]["fullpath"]

newProj = read(workspace_path)
```

Create a new testbench and file:
```Python
# create test bench file
newProj.createTestbench()

# create test bench config file
newProj.createTestbenchCfgFile()

# create test bench output file
# to save results of the extraction
newProj.createTestbenchOutputDir()
```


Show the information of the workspace projects and the library:
```Python
print(str(newLib))
print(str(newProj))
```
Output:
```
--------------------------------
Workspace Library:
--------------------------------
Workspace Name      :   new-project
Workspace Path      :   /foo/bar/
Workspace Full Path :   foo/bar/new-project.json
--------------------------------

--------------------------------
Workspace Name              : new-project
Parent Directory Path       : /foo/bar/
Technology File Path        : /foo/bar/sky130.tlef
Layout File Path            : /foo/bar/new_ic.gds
Circuit Netlist File Path   : 
Ports File Path             : 
Testbench File Path         : /foo/bar/testbench
Testbench Output Path       : /foo/bar/testbench/output
Testbench Configuration File: /foo/bar/testbench/cfg.toml
--------------------------------
```


This import is verified by an internal manager of created project workspaces, comparing them to the newly imported project. If the imported project exists in the creation database, the import will be successful, otherwise an exception will be raised.