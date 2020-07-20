import pytest
from requests import Response
from unittest.mock import patch, mock_open, MagicMock
from common.api import endpoints
from slave.slave import HyperSlave, Session, Task, List
from pickle import dumps as pickle_dumps
from zlib import compress
from common.task import TaskMessageType


class TestTasks:
    mock_url = 'http://mock_url.ca'

    def setup_method(self, method):
        """
        Before each
        """
        self.slave = HyperSlave()

    def teardown_method(self, method):
        """
        After each
        """

    @patch('slave.slave.Session', spec=Session)
    def test_req_task_endpoint(self, mock_session: Session):
        # Arrange
        mock_session.return_value = mock_session
        mock_session.get.return_value = False
        self.slave.host = "hostname"
        self.slave.port = "port"
        self.slave.job_id = 1234
        self.slave.session = mock_session
        expected_endpoint = f'http://{self.slave.host}:{self.slave.port}/{endpoints.GET_TASKS}/1234/1'
        # Act
        self.slave.req_tasks()
        # Assert
        mock_session.get.assert_called_with(expected_endpoint, timeout=5)

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_req_task(self, mock_session: Session, mock_resp: Response):
        # Arrange
        tasks = {"tasks": ["task_1"]}
        pickled_tasks = pickle_dumps(tasks)
        compressed_data = compress(pickled_tasks)
        mock_resp.data = compressed_data
        mock_session.return_value = mock_session
        mock_session.get.return_value = mock_resp
        self.slave.session = mock_session
        # Act
        tasks = self.slave.req_tasks()
        # Assert
        assert tasks == {'tasks': ['task_1']}

    @patch('slave.slave.Session', spec=Session)
    @patch('builtins.open', new_callable=mock_open(read_data='testing'))
    def test_handle_tasks_req_tasks(self, mock_session: Session, mock_file):
        # Arrange
        task_1: Task = Task(1, '', None, 'test.txt')
        task_1.message_type = TaskMessageType.TASK_RAW
        tasks: List[Task] = [task_1]

        mock_session.return_value = mock_session
        self.slave.req_tasks = MagicMock(return_value=tasks)
        self.slave.save_processed_data = MagicMock()
        self.slave.execute_tasks = MagicMock()
        self.slave.session = mock_session
        # Act
        self.slave.handle_tasks()
        # Assert
        self.slave.req_tasks.assert_called_with()

    @patch('slave.slave.Session', spec=Session)
    @patch('builtins.open', new_callable=mock_open(read_data='testing'))
    def test_handle_tasks_execute(self, mock_session: Session, mock_file):
        # Arrange
        task_1: Task = Task(1, '', None, 'test.txt')
        task_1.message_type = TaskMessageType.TASK_RAW
        tasks: List[Task] = [task_1]

        mock_session.return_value = mock_session
        self.slave.req_tasks = MagicMock(return_value=tasks)
        self.slave.save_processed_data = MagicMock()
        self.slave.execute_tasks = MagicMock()
        self.slave.session = mock_session
        # Act
        self.slave.handle_tasks()
        # Assert
        self.slave.execute_tasks.assert_called_with(tasks)

    @patch('slave.slave.Session', spec=Session)
    @patch('builtins.open', new_callable=mock_open(read_data='testing'))
    def test_handle_tasks_save_files(self, mock_session: Session, mock_file):
        # Arrange
        task_1: Task = Task(1, '', None, 'test.txt')
        task_1.message_type = TaskMessageType.TASK_RAW
        tasks: List[Task] = [task_1]

        mock_session.return_value = mock_session
        self.slave.req_tasks = MagicMock(return_value=tasks)
        self.slave.save_processed_data = MagicMock()
        self.slave.execute_tasks = MagicMock()
        self.slave.session = mock_session
        # Act
        self.slave.handle_tasks()
        # Assert
        self.save_processed_data.assert_called_with('task_1', 'test')

    # @patch('requests.Response', spec=Response)
    # @patch('slave.slave.Session', spec=Session)
    # # @patch('builtins.open', new_callable=mock_open)
    # def test_handle_tasks_file_creation(self, mock_session: Session, mock_resp: Response):
    #     # Arrange
    #     mock_resp.json.return_value = {"tasks": [{"id": "1", "data": "beep boop"}]}
    #     mock_session.return_value = mock_session
    #     mock_session.get.return_value = mock_resp
    #     self.slave.req_tasks = MagicMock()
    #     self.slave.save_processed_data = MagicMock()
    #     self.slave.execute_tasks = MagicMock()
    #     self.slave.session = mock_session
    #     # Act
    #     self.slave.handle_tasks()
    #     # Assert
    #     mock_file.assert_called_with(expected_arg, 'wb')
