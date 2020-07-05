import pytest
from unittest.mock import patch, mock_open
from master.master import HyperMaster, ConnectionManager, Path


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
        assert self.master.jobfile_name == 'jobfile'
        assert self.master.test_config is None
        assert self.master.task_queue == []
        assert self.master.jobfile_path is None
        assert self.master.job_path is None
        assert isinstance(self.master.conn_manager, ConnectionManager)

    @patch('builtins.open', new_callable=mock_open)
    @patch('master.master.json_loads')
    @patch('master.master.Path', spec=Path)
    def test_init_job(self, mock_path: Path, mock_json_loads, mock_file):
        # Arrange
        mock_path.cwd.return_value = Path("mock_path")
        job_root_dir_path = f'{Path.cwd()}/mock_path/job'
        jobfile_path = f'{job_root_dir_path}/{self.master.jobfile_name}'
        mock_path.exists.return_value = True
        mock_json_loads.return_value = {"job_id": 1, "file_names": ["file_name"]}
        # Act
        self.master.init_job()
        # Assert
        mock_file.assert_called_with(jobfile_path, 'r')
        assert self.master.jobfile_path == jobfile_path
        assert self.master.job_path == job_root_dir_path
