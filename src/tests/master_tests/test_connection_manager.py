import pytest
from master.connection import Connection, ConnectionDead, ConnectionManager


def test_add_get_connection():
    # Arrange
    connection_manager: ConnectionManager = ConnectionManager()
    connection_manager.connections_cleanup_timer.cancel()
    connection_manager.running = False
    connection_manager.add_connection('test_id')
    # Act
    connection = connection_manager.get_connection('test_id')
    connection.timer.cancel()
    # Assert
    assert(isinstance(connection, Connection))


def test_get_connection_exception_no_connection():
    # Arrange
    connection_manager: ConnectionManager = ConnectionManager()
    connection_manager.connections_cleanup_timer.cancel()
    connection_manager.running = False
    with pytest.raises(ConnectionDead):
        # Act and Assert
        assert connection_manager.get_connection('non_existent')


def test_get_connection_exception_dead_connection():
    # Arrange
    connection_manager: ConnectionManager = ConnectionManager()
    connection_manager.connections_cleanup_timer.cancel()
    connection_manager.running = False
    connection_manager.add_connection('dead_conn')
    connection: Connection = connection_manager.get_connection('dead_conn')
    connection.timer.cancel()
    # Act
    connection.timeout()
    with pytest.raises(ConnectionDead):
        # Assert
        assert connection_manager.get_connection('dead_conn')


def test_reset_connection_timer():
    # Arrange
    connection_manager: ConnectionManager = ConnectionManager()
    connection_manager.connections_cleanup_timer.cancel()
    connection_manager.running = False
    connection_manager.add_connection('test_id')
    connection: Connection = connection_manager.get_connection('test_id')
    connection.timer.cancel()
    # Act
    connection.reset_timer()
    # Assert
    assert(connection.timer.is_alive())
    connection.timer.cancel()


def test_cleanup_connections():
    # Arrange
    connection_manager: ConnectionManager = ConnectionManager()
    connection_manager.connections_cleanup_timer.cancel()
    connection_manager.running = False
    connection_manager.add_connection('test_conn_1')
    conn_1 = connection_manager.get_connection('test_conn_1')
    connection_manager.add_connection('test_conn_2')
    conn_2 = connection_manager.get_connection('test_conn_2')
    conn_1.timer.cancel()
    conn_2.timer.cancel()
    # Act
    conn_1.timeout()
    connection_manager.cleanup_connections()
    # Asserts
    with pytest.raises(ConnectionDead):
        assert(connection_manager.get_connection('test_conn_1'))
    assert(connection_manager.get_connection('test_conn_2'))
