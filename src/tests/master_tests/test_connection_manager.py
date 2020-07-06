import pytest
from master.connection import Connection, ConnectionDead, ConnectionManager


class TestConnectionManager:
    connection_manager: ConnectionManager

    def setup_method(self, method):
        """
        Before Each
        """
        self.connection_manager = ConnectionManager()
        self.connection_manager.connections_cleanup_timer.cancel()
        self.connection_manager.running = False

    def teardown_method(self, method):
        """
        After Each
        """
        self.connection_manager.connections_cleanup_timer.cancel()
        self.connection_manager.running = False

    def test_add_get_connection(self):
        # Arrange
        self.connection_manager.add_connection('test_id')
        # Act
        connection = self.connection_manager.get_connection('test_id')
        connection.timer.cancel()
        # Assert
        assert (isinstance(connection, Connection))

    def test_get_connection_exception_no_connection(self):
        with pytest.raises(ConnectionDead):
            # Act and Assert
            assert self.connection_manager.get_connection('non_existent')

    def test_get_connection_exception_dead_connection(self):
        # Arrange
        self.connection_manager.add_connection('dead_conn')
        connection: Connection = self.connection_manager.get_connection('dead_conn')
        connection.timer.cancel()
        # Act
        connection.timeout()
        with pytest.raises(ConnectionDead):
            # Assert
            assert self.connection_manager.get_connection('dead_conn')

    def test_reset_connection_timer(self):
        # Arrange
        self.connection_manager.add_connection('test_id')
        connection: Connection = self.connection_manager.get_connection('test_id')
        connection.timer.cancel()
        # Act
        self.connection_manager.reset_connection_timer('test_id')
        # Assert
        assert (connection.timer.is_alive())
        connection.timer.cancel()

    def test_reset_cleanup_connections_timer(self):
        # Arrange
        self.connection_manager.running = True
        self.connection_manager.connections_cleanup_timer.cancel()
        # Act
        self.connection_manager.cleanup_connections()
        # Assert
        assert (self.connection_manager.connections_cleanup_timer.is_alive())

    def test_cleanup_connections(self):
        # Arrange
        self.connection_manager.add_connection('test_conn_1')
        conn_1 = self.connection_manager.get_connection('test_conn_1')
        self.connection_manager.add_connection('test_conn_2')
        conn_2 = self.connection_manager.get_connection('test_conn_2')
        conn_1.timer.cancel()
        conn_2.timer.cancel()
        # Act
        conn_1.timeout()
        self.connection_manager.cleanup_connections()
        # Asserts
        with pytest.raises(ConnectionDead):
            assert (self.connection_manager.get_connection('test_conn_1'))
        assert (self.connection_manager.get_connection('test_conn_2'))
