import pytest
from common.networking import *

def test_working():
	ip = get_ip_addr()
	assert(ip)
