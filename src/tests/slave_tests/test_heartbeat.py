import pytest
from requests import Response, Session, exceptions as RequestExceptions
from unittest.mock import MagicMock
from time import sleep
from slave.heartbeat import Heartbeat


class TestHeartbeat:
    mock_url = 'https://mock_url.ca'

    def setup_method(self, method):
        """
        Before Each
        """
        self.mock_response = Response()
        self.mock_response.status_code = 200
        self.mock_session = Session
        self.mock_session.get = MagicMock(return_value=self.mock_response)
        self.heartbeat = Heartbeat(self.mock_session, self.mock_url)

    def teardown_method(self, method):
        """
        After Each
        """
        self.heartbeat.timer.cancel()

    def test_send_beat(self):
        # Act
        self.heartbeat.send_beat()
        # Assert
        assert (self.heartbeat.fails == 0)

    def test_start_beating(self):
        # Arrange
        self.heartbeat.timer.cancel()
        # Act
        self.heartbeat.start_beating()
        # Assert
        assert (self.heartbeat.timer.is_alive())

    def test_reset_timer(self):
        # Arrange
        self.heartbeat.timer.cancel()
        # Act
        self.heartbeat.reset_timer()
        # Assert
        assert (self.heartbeat.timer.is_alive())

    def test_stop_beating(self):
        # Act
        self.heartbeat.stop_beating()
        # Assert
        assert (not self.heartbeat.timer.is_alive())

    def test_retry_attempts(self):
        # Arrange
        self.mock_response.status_code = 500
        self.mock_session.get = MagicMock(return_value=self.mock_response)
        self.heartbeat = Heartbeat(self.mock_session, self.mock_url, interval_secs=0.0, retry_attempts=0)
        # Act
        self.heartbeat.start_beating()
        sleep(0.000000000005)
        # Assert
        assert (self.heartbeat.fails == 1)
        assert (not self.heartbeat.timer.is_alive())

    def test_catch_generic_exception(self):
        # Arrange
        self.mock_response = None
        self.mock_session.get = MagicMock(side_effect=Exception("Mock Error. Ignore Me."))
        self.heartbeat = Heartbeat(self.mock_session, self.mock_url, interval_secs=0.0, retry_attempts=0)
        with pytest.raises(Exception):
            # Act and Assert
            assert self.heartbeat.start_beating()

    def test_catch_generic_exception(self):
        # Arrange
        self.mock_response = None
        self.mock_session.get = MagicMock(side_effect=Exception("Mock Error. Ignore Me."))
        self.heartbeat = Heartbeat(self.mock_session, self.mock_url, interval_secs=0.0, retry_attempts=0)
        with pytest.raises(Exception):
            # Act and Assert
            assert self.heartbeat.start_beating()

    def test_catch_connection_error(self):
        # Arrange
        self.mock_response = None
        self.mock_session.get = MagicMock(side_effect=(RequestExceptions.ConnectionError, ConnectionError))
        self.heartbeat = Heartbeat(self.mock_session, self.mock_url, interval_secs=0.0, retry_attempts=0)
        with pytest.raises(Exception):
            # Act and Assert
            assert self.heartbeat.start_beating()
