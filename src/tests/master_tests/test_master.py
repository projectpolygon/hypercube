import pytest
from unittest.mock import patch, mock_open
from master.master import HyperMaster, ConnectionManager, Path, TaskManager, JobInfo


class TestMaster:

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
        assert self.master.task_queue == []
        assert isinstance(self.master.task_manager, TaskManager)
        assert isinstance(self.master.conn_manager, ConnectionManager)
        assert isinstance(self.master.job, JobInfo)

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
