import pytest
from unittest.mock import patch, mock_open, MagicMock
from requests import Response
from random import random
from common.api import endpoints
from slave.slave import HyperSlave, Path, Session, Heartbeat, CompressionException


class TestSlave:

    def setup_method(self, method):
        """
        Before Each
        """
        self.slave = HyperSlave()

    def teardown_method(self, method):
        """
        After Each
        """

    def test_default_values(self):
        assert self.slave.heartbeat is None
        assert self.slave.session is None
        assert self.slave.ip_addr is None
        assert self.slave.host is None
        assert self.slave.port == 5678
        assert self.slave.job_id is None
        assert self.slave.job_path is None
        assert self.slave.master_info is None
        assert self.slave.running is True

    @patch('slave.slave.Path')
    def test_init_job_root(self, mock_path: Path):
        # Arrange
        mock_path.cwd.return_value = Path("mock_path")
        expected_path = f'{Path.cwd()}/mock_path/job'
        # Act
        self.slave.init_job_root()
        # Assert
        assert self.slave.job_path == expected_path

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_connect_resp_200(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.status_code = 200
        mock_resp.json.return_value = "mock_json"
        mock_session.get.return_value = mock_resp
        # Act
        session = self.slave.connect("hostname", "port")
        # Assert
        assert session == mock_session

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_connect_resp_not_ok(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.status_code = 500
        mock_session.get.return_value = mock_resp
        # Act
        session = self.slave.connect("hostname", "port")
        # Assert
        assert session is None

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_connect_invalid_json(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError
        mock_session.get.return_value = mock_resp

        with pytest.raises(Exception):
            # Act & Assert
            assert self.slave.connect("hostname", "port")

    @patch('slave.slave.Session', spec=Session)
    def test_connect_connection_error(self, mock_session: Session):
        # Arrange
        mock_session.return_value = mock_session
        mock_session.get.side_effect = ConnectionError
        # Act
        ret = self.slave.connect("hostname", "port")
        # Assert
        assert ret is None

    @patch('slave.slave.Session', spec=Session)
    def test_connect_generic_exception(self, mock_session: Session, capsys):
        # Arrange
        mock_session.return_value = mock_session
        mock_session.get.side_effect = Exception("Mock Error. Ignore Me!")
        with pytest.raises(SystemExit):
            # Act & Assert
            assert self.slave.connect("hostname", "port")

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_attempt_master_connection(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.status_code = 200
        mock_session.get.return_value = mock_resp
        mock_session.cookies = MagicMock()
        # Act
        self.slave.attempt_master_connection(5678)
        # Assert
        assert self.slave.session == mock_session

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_attempt_master_connection_none(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.status_code = 500
        # Act
        ret = self.slave.attempt_master_connection(5678)
        # Assert
        assert ret is None

    @patch('random.random', spec=random)
    @patch('slave.slave.Session', spec=Session)
    def test_set_session(self, mock_session: Session, mock_random):
        # Arrange
        mock_random.return_value = 1
        mock_session.return_value = mock_session
        mock_session.cookies = MagicMock()
        self.slave.ip_addr = "123.4567.8910"
        # Act
        self.slave.set_session(mock_session)
        cookie = mock_session.cookies.set_cookie.call_args[0][0].value
        # Assert
        assert self.slave.ip_addr in cookie

    @patch('slave.slave.rmtree')
    @patch('slave.slave.Path')
    def test_create_job_dir(self, mock_path: Path, mock_rmtree):
        # Arrange
        self.slave.job_path = "test_job_path"
        self.slave.job_id = "test_job_id"
        expected_data = f'{self.slave.job_path}/{self.slave.job_id}'
        # Act
        actual_data = self.slave.create_job_dir()
        # Assert
        assert expected_data == actual_data

    @patch('builtins.open', new_callable=mock_open)
    def test_save_processed_data(self, mock_file):
        # Arrange
        self.slave.job_path = "test_job_path"
        self.slave.job_id = "test_job_id"
        test_file_data = "test_file_data"
        test_file_name = "test_file_name"
        expected_arg = f'{self.slave.job_path}/{self.slave.job_id}/{test_file_name}'
        # Act
        self.slave.save_processed_data(test_file_name, test_file_data)
        # Assert
        mock_file.assert_called_with(expected_arg, 'wb')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_processed_data_catch_exception(self, mock_file):
        # Arrange
        mock_file.side_effect = OSError('Mock Error. Ignore Me!')
        with pytest.raises(Exception):
            # Act & Assert
            assert self.slave.save_processed_data("test_file_name", "test_file_data")

    @patch('slave.slave.decompress')
    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_get_file_endpoint(self, mock_session: Session, mock_resp: Response, mock_decompress):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.status_code = 200
        mock_resp.json.return_value = "mock_json"
        mock_session.get.return_value = mock_resp
        job_id = "123"
        file_name = "filename"
        hostname = "hostname"
        port = "port"
        expected_endpoint = f'http://{hostname}:{port}/{endpoints.FILE}/{job_id}/{file_name}'
        self.slave.host = hostname
        self.slave.port = port
        self.slave.session = mock_session
        self.slave.job_id = job_id
        self.slave.save_processed_data = MagicMock()
        # Act
        success = self.slave.get_file(file_name)
        # Assert
        mock_session.get.assert_called_with(expected_endpoint)
        assert success

    @patch('slave.slave.Session', spec=Session)
    def test_get_file_no_resp(self, mock_session: Session):
        # Arrange
        mock_session.return_value = mock_session
        mock_session.get.return_value = False
        self.slave.session = mock_session
        # Act
        success = self.slave.get_file("file_name")
        # Assert
        assert not success

    @patch('slave.slave.decompress')
    @patch('slave.slave.Session', spec=Session)
    def test_get_file_decompress_exception(self, mock_session: Session, mock_decompress):
        # Arrange
        mock_session.return_value = mock_session
        mock_session.get.return_value = MagicMock()
        self.slave.session = mock_session
        mock_decompress.side_effect = CompressionException
        # Act
        success = self.slave.get_file("file_name")
        # Assert
        assert not success

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_req_job_endpoint(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_session.get.return_value = False
        self.slave.host = "hostname"
        self.slave.port = "port"
        self.slave.session = mock_session
        expected_endpoint = f'http://{self.slave.host}:{self.slave.port}/{endpoints.JOB}'
        # Act
        self.slave.req_job()
        # Assert
        mock_session.get.assert_called_with(expected_endpoint, timeout=5)

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_req_job(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_resp.json.return_value = '{"job_id": 1, "file_names": ["file_name"]}'
        mock_session.return_value = mock_session
        mock_session.get.return_value = mock_resp
        self.slave.create_job_dir = MagicMock()
        self.slave.get_file = MagicMock()
        self.slave.handle_tasks = MagicMock()
        self.slave.heartbeat = MagicMock()
        self.slave.process_job = MagicMock(return_value=False)
        self.slave.session = mock_session
        # Act
        self.slave.req_job()
        # Assert
        self.slave.get_file.assert_called_with('file_name')

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_req_job_value_error(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.json.side_effect = ValueError
        mock_session.get.return_value = mock_resp
        self.slave.session = mock_session
        # Act & Assert
        with pytest.raises(Exception):
            assert self.slave.req_job()

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_req_job_generic_exception(self, mock_session: Session, mock_resp: Response):
        # Arrange
        mock_session.return_value = mock_session
        mock_resp.json.side_effect = Exception("Mock Error. Ignore Me!")
        mock_session.get.return_value = mock_resp
        self.slave.session = mock_session
        # Act & Assert
        with pytest.raises(Exception):
            assert self.slave.req_job()

    def test_start(self):
        # Arrange
        self.slave.init_job_root = MagicMock()
        self.slave.attempt_master_connection = MagicMock(return_value="hostname")
        self.slave.req_job = MagicMock()
        expected_url = f'http://hostname:{self.slave.port}/{endpoints.HEARTBEAT}'
        # Act
        self.slave.start()
        # Assert
        assert self.slave.heartbeat.url == expected_url
