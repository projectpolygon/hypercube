import pytest
from master.status_manager import StatusManager


class TestStatusManager:

    def setup_method(self, method):
        """
        Before Each
        """
        self.status_manager = StatusManager()

    def test_initial_status(self):
        assert self.status_manager.status.num_tasks == 0
        assert self.status_manager.status.num_slaves == 0
        assert self.status_manager.status.num_tasks_done == 0
        assert not self.status_manager.status.job_done

    def test_new_slave_connected(self):
        # Arrange
        initial_data = 419
        self.status_manager.status.num_slaves = initial_data
        expected_data = 420
        # Act
        self.status_manager.new_slave_connected()
        # Assert
        assert self.status_manager.status.num_slaves == expected_data

    def test_slave_disconnected(self):
        # Arrange
        initial_data = 420
        self.status_manager.status.num_slaves = initial_data
        expected_data = 419
        # Act
        self.status_manager.slave_disconnected()
        # Assert
        assert self.status_manager.status.num_slaves == expected_data

    def test_tasks_loaded(self):
        # Arrange
        expected_data = 420
        # Act
        self.status_manager.tasks_loaded(expected_data)
        # Assert
        assert self.status_manager.status.num_tasks == expected_data

    def test_tasks_loaded_value_error(self):
        # Arrange
        expected_data = 420
        self.status_manager.status.num_tasks = expected_data
        # Act & Assert
        with pytest.raises(ValueError):
            assert self.status_manager.tasks_loaded(0)
        assert self.status_manager.status.num_tasks == expected_data

    def test_tasks_completed(self):
        # Arrange
        initial_data = 400
        self.status_manager.status.num_tasks = initial_data + 30
        self.status_manager.status.num_tasks_done = initial_data
        expected_data = 420
        # Act
        self.status_manager.tasks_completed(20)
        # Assert
        assert self.status_manager.status.num_tasks_done == expected_data

    def test_tasks_completed_value_error(self):
        # Arrange
        expected_data = 420
        self.status_manager.status.num_tasks_done = expected_data
        # Act & Assert
        with pytest.raises(ValueError):
            assert self.status_manager.tasks_completed(0)
        assert self.status_manager.status.num_tasks_done == expected_data

    def test_job_completed(self):
        # Arrange
        self.status_manager.status.job_done = False
        # Act
        self.status_manager.job_completed()
        # Assert
        assert self.status_manager.status.job_done

    def test_is_job_done(self):
        # Arrange
        self.status_manager.status.job_done = True
        # Act & Assert
        assert self.status_manager.is_job_done()

    def test_get_status(self):
        # Arrange
        expected_data = 'Connected Slaves: 1\n'
        expected_data += 'Tasks Done: 312\n'
        expected_data += 'Total Tasks: 410\n'
        expected_data += 'Progress: 76.10%\n'
        expected_data += 'Job Completed: False'
        self.status_manager.new_slave_connected()
        self.status_manager.tasks_loaded(410)
        self.status_manager.tasks_completed(312)
        # Act
        actual_data = self.status_manager.get_status()
        # Assert
        assert actual_data == expected_data

    def test_print_status(self, capsys):
        # Arrange
        self.status_manager.new_slave_connected()
        self.status_manager.tasks_loaded(410)
        self.status_manager.tasks_completed(312)
        expected_data = self.status_manager.get_status()
        # Act
        self.status_manager.print_status()
        captured = capsys.readouterr()
        # Assert
        assert expected_data in captured.out
