import pytest
from master.master import HyperMaster

def test_working():
    master = HyperMaster()
    assert(master)
