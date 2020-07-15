import pytest
from unittest.mock import patch, mock_open
from master.master import HyperMaster, ConnectionManager, Path, \
    TaskManager, JobInfo, create_app, compress, decompress, Response, \
    CompressionException, BytesIO, pickle_dumps, pickle_loads, PicklingError, UnpicklingError, \
    JobNotInitialized, Task, List, endpoints


class TestMaster:

    def get_test_client(self):
        app = create_app(self.master)
        return app.test_client()

    def setup_method(self):
        """
        Before Each
        """
        self.master = HyperMaster()

    def teardown_method(self, method):
        """
        After Each
        """

    def test_default_values(self):
        assert self.master.host == '0.0.0.0'
        assert self.master.port == 5678
        assert self.master.test_config is None
        assert isinstance(self.master.task_manager, TaskManager)
        assert isinstance(self.master.conn_manager, ConnectionManager)
        assert isinstance(self.master.job, JobInfo)

    def test_load_tasks(self):
        # Arrange
        self.master.job.job_id = 1234
        tasks: List[Task] = [Task(1, '', None, ''), Task(2, '', None, ''), Task(3, '', None, '')]
        available_tasks = self.master.task_manager.available_tasks
        # Act
        self.master.load_tasks(tasks)
        # Assert
        assert available_tasks.qsize() == len(tasks)
        while not available_tasks.empty():
            assert available_tasks.get() in tasks

    def test_load_tasks_job_uninitialized(self):
        # Arrange
        tasks: List[Task] = []
        with pytest.raises(JobNotInitialized):
            # Act and Assert
            assert self.master.load_tasks(tasks)

    @patch('master.master.Path', spec=Path)
    def test_init_job(self, mock_path: Path):
        # Arrange
        job = JobInfo()
        job.job_id = None
        job.job_path = '/mock_path/job'
        job.file_names = ['file_name1', 'file_name2']
        mock_path.exists.return_value = True
        # Act
        self.master.init_job(job)
        # Assert
        assert isinstance(self.master.job.job_id, int)

    def test_get_job(self):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.job.job_path = 123456
        # Act
        resp: Response = test_client.get(f'/{endpoints.JOB}')
        # Assert
        assert '123456' in resp.json
        assert "test_session_id" in self.master.conn_manager.connections.keys()

    @patch('builtins.open', new_callable=mock_open)
    def test_get_file(self, mock_file):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        self.master.job.job_path = 'mock_job_path'
        expected_data = bytes(0b1010)
        mock_file.return_value.read.return_value = expected_data
        # Act
        resp: Response = test_client.get(f'/{endpoints.FILE}/1234/file_name')
        # Assert
        assert decompress(resp.data) == expected_data

    def test_get_file_wrong_job_error(self):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        # Act
        resp: Response = test_client.get(f'/{endpoints.FILE}/0/file_name')
        # Assert
        assert resp.status_code == 403

    def test_get_file_uninitialized_job_error(self):
        # Arrange
        test_client = self.get_test_client()
        # Act
        resp: Response = test_client.get(f'/{endpoints.FILE}/0/file_name')
        # Assert
        assert resp.status_code == 403

    @patch('master.master.compress')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_file_compression_error(self, mock_file, mock_compress):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        self.master.job.job_path = 'mock_job_path'
        mock_compress.side_effect = CompressionException
        # Act
        resp: Response = test_client.get(f'/{endpoints.FILE}/1234/file_name')
        # Assert
        assert resp.status_code == 500

    @patch('builtins.open', new_callable=mock_open)
    def test_get_file_file_not_found_error(self, mock_file):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        self.master.job.job_path = 'mock_job_path'
        mock_file.side_effect = FileNotFoundError
        # Act
        resp: Response = test_client.get(f'/{endpoints.FILE}/1234/file_name')
        # Assert
        assert resp.status_code == 404

    @patch('builtins.open', new_callable=mock_open)
    def test_get_file_generic_error(self, mock_file):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        self.master.job.job_path = 'mock_job_path'
        mock_file.side_effect = Exception("Mock Error. Ignore Me!")
        # Act
        resp: Response = test_client.get(f'/{endpoints.FILE}/1234/file_name')
        # Assert
        assert resp.status_code == 501

    def test_get_tasks(self):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.job.job_id = 1234
        tasks: List[Task] = [Task(1, '', None, ''), Task(2, '', None, ''), Task(3, '', None, '')]
        for task in tasks:
            task.set_job(1234)
        self.master.task_manager.add_new_available_tasks(tasks, 1234)
        # Act
        resp: Response = test_client.get(f'/{endpoints.GET_TASKS}/1234/2')
        # Assert
        actual_data: List[Task] = pickle_loads(decompress(resp.data))
        assert len(actual_data) == 2
        assert actual_data == tasks[0:2]

    @patch('master.master.pickle_dumps')
    def test_get_tasks_pickle_error(self, mock_pickle_dumps):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.job.job_id = 1234
        tasks: List[Task] = [Task(1, '', None, ''), Task(2, '', None, ''), Task(3, '', None, '')]
        self.master.task_manager.add_new_available_tasks(tasks, 1234)
        mock_pickle_dumps.side_effect = PicklingError
        # Act
        resp: Response = test_client.get(f'/{endpoints.GET_TASKS}/1234/2')
        # Assert
        assert resp.status_code == 500

    @patch('master.master.compress')
    def test_get_tasks_compression_error(self, mock_compress):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.job.job_id = 1234
        tasks: List[Task] = [Task(1, '', None, ''), Task(2, '', None, ''), Task(3, '', None, '')]
        self.master.task_manager.add_new_available_tasks(tasks, 1234)
        mock_compress.side_effect = CompressionException
        # Act
        resp: Response = test_client.get(f'/{endpoints.GET_TASKS}/1234/2')
        # Assert
        assert resp.status_code == 500

    def test_get_tasks_wrong_job_error(self):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.job.job_id = 1234
        task: Task = Task(1, '', None, '')
        self.master.task_manager.add_new_available_task(task, 1234)
        # Act
        resp: Response = test_client.get(f'/{endpoints.GET_TASKS}/0/2')
        # Assert
        assert resp.status_code == 403

    def test_get_tasks_uninitialized_job_error(self):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        task: Task = Task(1, '', None, '')
        self.master.task_manager.add_new_available_task(task, 1234)
        # Act
        resp: Response = test_client.get(f'/{endpoints.GET_TASKS}/1234/2')
        # Assert
        assert resp.status_code == 403

    def test_get_tasks_generic_error(self):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.job.job_id = 1234
        # Act
        resp: Response = test_client.get(f'/{endpoints.GET_TASKS}/1234/2')
        # Assert
        assert resp.status_code == 501

    def test_tasks_done(self):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.job.job_id = 1234
        task: Task = Task(1, '', None, '')
        task.set_job(1234)
        self.master.load_tasks([task])
        resp1: Response = test_client.get(f'/{endpoints.GET_TASKS}/1234/2')
        data = resp1.data
        # Act
        resp2: Response = test_client.post(f'/{endpoints.TASKS_DONE}/1234', data=data)
        # Assert
        assert resp2.status_code == 200
        assert self.master.task_manager.finished_tasks.qsize() == 1
        assert self.master.task_manager.finished_tasks.get() == task

    def test_tasks_done_job_uninitialized_error(self):
        # Arrange
        test_client = self.get_test_client()
        # Act
        resp2: Response = test_client.post(f'/{endpoints.TASKS_DONE}/1234')
        # Assert
        assert resp2.status_code == 403

    def test_tasks_done_wrong_job_error(self):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        # Act
        resp2: Response = test_client.post(f'/{endpoints.TASKS_DONE}/0')
        # Assert
        assert resp2.status_code == 403

    @patch('master.master.decompress')
    def test_tasks_done_compression_error(self, mock_decompress):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        mock_decompress.side_effect = CompressionException
        # Act
        resp: Response = test_client.post(f'/{endpoints.TASKS_DONE}/1234')
        # Assert
        assert resp.status_code == 500

    @patch('master.master.decompress')
    @patch('master.master.pickle_loads')
    def test_tasks_done_unpickle_error(self, mock_pickle_loads, mock_decompress):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        mock_decompress.return_value = True
        mock_pickle_loads.side_effect = UnpicklingError
        # Act
        resp: Response = test_client.post(f'/{endpoints.TASKS_DONE}/1234')
        # Assert
        assert resp.status_code == 500

    @patch('master.master.decompress')
    @patch('master.master.pickle_loads')
    def test_tasks_done_generic_error(self, mock_pickle_loads, mock_decompress):
        # Arrange
        test_client = self.get_test_client()
        self.master.job.job_id = 1234
        mock_decompress.return_value = True
        mock_pickle_loads.side_effect = Exception("Mock Error. Ignore Me!")
        # Act
        resp: Response = test_client.post(f'/{endpoints.TASKS_DONE}/1234')
        # Assert
        assert resp.status_code == 501

    def test_discovery(self):
        # Arrange
        test_client = self.get_test_client()
        # Act
        resp: Response = test_client.get(f'/{endpoints.DISCOVERY}')
        # Assert
        assert resp.status_code == 200
        assert 'ip' in resp.json

    def test_heartbeat(self):
        # Arrange
        test_client = self.get_test_client()
        test_client.set_cookie('server', 'id', 'test_session_id')
        self.master.conn_manager.add_connection("test_session_id")
        # Act
        resp: Response = test_client.get(f'/{endpoints.HEARTBEAT}')
        # Assert
        assert resp.status_code == 200
