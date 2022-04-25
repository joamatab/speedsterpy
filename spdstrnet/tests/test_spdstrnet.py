import unittest
from spdstrnet import __version__
from spdstrnet import *

def test_version():
    assert __version__ == '0.1.0'

class TestGeometry(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()