from speedster_py import __version__


def test_version():
    assert __version__ == '0.1.2'
    assert __author__ == 'Diogo André Silvares Dias'
    assert __annotations__ == 'Affiliations : \
                               NOVA University of Lisbon, \
                               School of Science and Technology (SST)'
