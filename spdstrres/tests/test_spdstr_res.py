import sys

sys.path.append("../spdstrres")
from spdstrres import (
    __version__,
)


def test_version():
    assert __version__ == "0.1.2"
