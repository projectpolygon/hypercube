import pytest
from master.connection import Connection, ConnectionDead


def test_timeout():
    # Arrange
    connection = Connection('test_id')
    connection.timer.cancel()
    # Act
    connection.timeout()
    # Assert
    assert(not connection.is_alive())


def test_is_alive():
    # Arrange
    connection = Connection('test_id')
    connection.timer.cancel()
    # Act and Assert
    assert(connection.is_alive())


def test_reset_timer():
    # Arrange
    connection = Connection('test_id')
    connection.timer.cancel()
    # Act
    connection.reset_timer()
    # Assert
    assert(connection.timer.is_alive())
    connection.timer.cancel()


def test_reset_timer_exception():
    # Arrange
    connection = Connection('test_id')
    connection.timer.cancel()
    # Assert
    connection.timeout()
    with pytest.raises(ConnectionDead):
        # Assert
        assert connection.reset_timer()
