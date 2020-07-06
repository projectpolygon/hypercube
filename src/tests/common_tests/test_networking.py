import pytest
from unittest.mock import patch
from common.networking import SocketError, socket, get_ip_addr


class TestGetIpAdd:

    def test_smoke(self):
        ip = get_ip_addr()
        assert ip

    def test_catch_exception(self):
        # Arrange
        with patch.object(socket, "connect", side_effect=SocketError):
            ip = get_ip_addr()
            assert ip == '127.0.0.1'

