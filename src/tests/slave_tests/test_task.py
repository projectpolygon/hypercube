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
        self.slave.req_tasks(1)
        # Assert
        mock_session.get.assert_called_with(expected_endpoint, timeout=5)

    @patch('requests.Response', spec=Response)
    @patch('slave.slave.Session', spec=Session)
    def test_req_task(self, mock_session: Session, mock_resp: Response):
        # Arrange
        expected_tasks: List[Task] = [Task(1, "", [], None, "", "")]
        pickled_tasks = pickle_dumps(expected_tasks)
        compressed_data = compress(pickled_tasks)
        mock_resp.status_code = 69
        mock_resp.content = compressed_data
        mock_session.return_value = mock_session
        mock_session.get.return_value = mock_resp
        self.slave.session = mock_session
        # Act
        actual_tasks = self.slave.req_tasks(1)
        # Assert
        assert expected_tasks[0].task_id == actual_tasks[0].task_id

    @patch('slave.slave.run_shell_command', return_value=0)
    @patch('slave.slave.Session', spec=Session)
    def test_execute_tasks_passed(self, mock_session: Session, mock_run_shell_command):
        # Arrange
        task_1: Task = Task(1, "echo hello_world", [], None, "result.txt", 'payload.txt')
        task_1.message_type = TaskMessageType.TASK_RAW
        tasks: List[Task] = [task_1]
        mock_session.return_value = mock_session
        # Act
        failed_tasks = self.slave.execute_tasks(tasks)
        # Assert
        assert failed_tasks == []

    @patch('slave.slave.run_shell_command', return_value=1)
    @patch('slave.slave.Session', spec=Session)
    def test_execute_tasks_failed(self, mock_session: Session, mock_run_shell_command):
        # Arrange
        task_1: Task = Task(1, "", [], None, "result.txt", 'payload.txt')
        task_1.message_type = TaskMessageType.TASK_RAW
        tasks: List[Task] = [task_1]
        mock_session.return_value = mock_session
        self.slave.run_shell_command = MagicMock(return_value=1)
        # Act
        failed_tasks = self.slave.execute_tasks(tasks)
        # Assert
        assert failed_tasks == [task_1]

    @patch('slave.slave.Session', spec=Session)
    @patch('builtins.open', new_callable=mock_open(read_data='testing'))
    def test_handle_tasks_save_files(self, mock_session: Session, mock_file):
        # Arrange
        expected_payload = "Test".encode()
        task_1: Task = Task(1, "", [], expected_payload, "result.txt", 'payload.txt')
        task_1.message_type = TaskMessageType.TASK_RAW
        tasks: List[Task] = [task_1]

        mock_session.return_value = mock_session
        self.slave.req_tasks = MagicMock(return_value=tasks)
        self.slave.save_processed_data = MagicMock()
        self.slave.execute_tasks = MagicMock()
        self.slave.session = mock_session
        # Act
        self.slave.handle_tasks(tasks)
        # Assert
        self.slave.execute_tasks.assert_called_with(tasks)
        self.slave.save_processed_data.assert_called_with('payload.txt', expected_payload)

    def test_handle_process_job(self):
        # Arrange
        expected_payload = "Test".encode()
        task_1: Task = Task(1, "", [], expected_payload, "result.txt", 'payload.txt')
        task_1.message_type = TaskMessageType.TASK_RAW
        tasks: List[Task] = [task_1]

        self.slave.req_tasks = MagicMock(return_value=tasks)
        self.slave.handle_tasks = MagicMock(return_value=(True, tasks))
        self.slave.send_tasks = MagicMock()
        # Act
        self.slave.process_job()
        # Assert
        self.slave.req_tasks.assert_called_with(1)
        self.slave.handle_tasks.assert_called_with(tasks)

    def test_handle_process_job_no_task(self):
        # Arrange
        self.slave.req_tasks = MagicMock(return_value=None)
        self.slave.handle_tasks = MagicMock(return_value=(False, []))
        self.slave.send_tasks = MagicMock()
        # Act
        success = self.slave.process_job()
        # Assert
        assert not success
