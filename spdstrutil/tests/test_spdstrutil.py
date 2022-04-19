import sys
sys.path.append("../spdstrutil")
from spdstrutil import (
    __version__,
    GdsLayerPurpose,
    GdsTable,
    readGdsTable,
    writeGdsTable,
    getFromPurpose,
)

def test_version():
    assert __version__ == '0.1.0'

def test_gds_table_read():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/resources/sky130/skywater-pdk-libs-sky130_fd_pr/skywater130/gds_layers.csv"
    gdsTab = readGdsTable(path)
    assert type(gdsTab) == GdsTable
    #print(str(gdsTab))
    
def test_gds_table_write():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrutil/resources"
    gdsTab = GdsTable()
    gdsTab.add(
        layer = 71,
        dataType = 20,
        name = "met4",
        purpose = [GdsLayerPurpose.DRAWING.name, GdsLayerPurpose.TEXT.name],
        description = "Metal 4"
    )
    writeGdsTable(gdsTab, path)
    #print(str(gdsTab))

def test_gds_table_read_yaml():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrutil/resources/gds_table.yaml"
    gdsTab = readGdsTable(path)
    #print(str(gdsTab))

def test_filter_gds_table_by_purpose():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/resources/sky130/skywater-pdk-libs-sky130_fd_pr/skywater130/gds_layers.csv"
    gdsTab = readGdsTable(path)
    print(str(gdsTab))
    newtab = getFromPurpose(gdsTab, GdsLayerPurpose.DRAWING)
    print(str(newtab))