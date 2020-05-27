import pytest
from slave.slave import HyperSlave

def test_working():
	slave = HyperSlave()
	assert(slave)
