import pytest
from master.connection import Connection, ConnectionDead

def test_timeout():
    connection = Connection('test_id')
    connection.timer.cancel()
    connection.timeout()
    assert(not connection.is_alive())

def test_is_alive():
    connection = Connection('test_id')
    connection.timer.cancel()
    assert(connection.is_alive())

def test_reset_timer():
    connection = Connection('test_id')
    connection.timer.cancel()
    connection.reset_timer()
    assert(connection.timer.is_alive())
    connection.timer.cancel()

def test_reset_timer_exception():
    connection = Connection('test_id')
    connection.timer.cancel()
    connection.timeout()
    with pytest.raises(ConnectionDead):
        assert connection.reset_timer()
