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
|   |--output/
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
Create a new Project Library:
```Python
newProj = SpdstrProject("new-project") # name the workspace: "new-project"
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
```

Export the workspace directory tree to JSON or toml:
```Python
# export to .json (default)
spdstrlib.write(newProj, 'json')
#or
spdstrlib.write(newProj)

# export to .toml
sdstrlib.write(newProj, 'toml')
``` 

Import the workspace to the application:
```Python
workspace_path = "foo/bar/new-project.json"
#or 
# workspace_path = "foo/bar/new-project.toml"
newProj = spdstrlib.read(workspace_path)
```

This import is verified by an internal manager of created project workspaces, comparing them to the newly imported project. If the imported project exists in the creation database, the import will be successful, otherwise an exception will be raised.