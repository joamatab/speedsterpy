import sys
sys.path.append("../spdstrutil")
from spdstrutil import (
    __version__,
    GdsLayerPurpose,
    GdsTable,
    readGdsTable,
    writeGdsTable,
    getGdsTableEntriesFromPurpose,
    getGdsTableEntriesFromLayerName,
    getGdsLayerDatatypeFromLayerNamePurpose,
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
    assert True
    #print(str(gdsTab))

def test_gds_table_read_yaml():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/spdstrutil/resources/gds_table.yaml"
    gdsTab = readGdsTable(path)
    #print(str(gdsTab))
    assert True

def test_filter_gds_table_by_purpose():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/resources/sky130/skywater-pdk-libs-sky130_fd_pr/skywater130/gds_layers.csv"
    gdsTab = readGdsTable(path)
    #print(str(gdsTab))
    newtab = getGdsTableEntriesFromPurpose(gdsTab, GdsLayerPurpose.DRAWING)
    print(str(newtab))
    assert True

def test_filter_gds_table_by_layer_name():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/resources/sky130/skywater-pdk-libs-sky130_fd_pr/skywater130/gds_layers.csv"
    gdsTab = readGdsTable(path)
    #print(str(gdsTab))
    newtab = getGdsTableEntriesFromLayerName(gdsTab, "met4")
    print(str(newtab))
    assert True

def test_get_gds_layer_datatype_from_layer_name_purpose():
    path = "/Users/dasdias/Documents/SoftwareProjects/speedsterpy/resources/sky130/skywater-pdk-libs-sky130_fd_pr/skywater130/gds_layers.csv"
    gdsTab = readGdsTable(path)
    #print(str(gdsTab))
    datatype = getGdsLayerDatatypeFromLayerNamePurpose(gdsTab, "met4", GdsLayerPurpose.PIN)
    print(datatype)
    assert True
    
    