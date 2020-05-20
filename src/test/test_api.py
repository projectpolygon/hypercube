import pytest
from common.message import *

def test_working():
	new_msg = Message(MessageType.JOB_REQUEST)
	assert(new_msg)
