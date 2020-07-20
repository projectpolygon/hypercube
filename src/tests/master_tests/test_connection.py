import pytest
from master.connection_manager import Connection, ConnectionDead


class TestConnection:
    connection: Connection

    def setup_method(self, method):
        """
        Before Each
        """
        self.connection = Connection('test_id')
        self.connection.timer.cancel()

    def teardown_method(self, method):
        """
        After Each
        """
        self.connection.timer.cancel()

    def test_timeout(self):
        # Act
        self.connection.timeout()
        # Assert
        assert (not self.connection.is_alive())

    def test_is_alive(self):
        # Act and Assert
        assert (self.connection.is_alive())

    def test_reset_timer(self):
        # Act
        self.connection.reset_timer()
        # Assert
        assert (self.connection.timer.is_alive())

    def test_reset_timer_exception(self):
        # Act
        self.connection.timeout()
        with pytest.raises(ConnectionDead):
            # Assert
            assert self.connection.reset_timer()

    def test_equality(self):
        # Arrange/Act
        conn2 = self.connection
        # Assert
        assert conn2 == self.connection

    def test_inequality_same_type(self):
        # Arrange/Act
        conn2 = Connection("test_id_2")
        assert conn2 != self.connection

    def test_inequality_different_type(self):
        # Arrange
        conn2 = "str"
        with pytest.raises(Exception):
            # Act and Assert
            assert conn2 != self.connection
