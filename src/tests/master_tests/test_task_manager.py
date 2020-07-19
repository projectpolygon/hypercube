import pytest
from common.task import Task
from master.status_manager import StatusManager
from master.task_manager import TaskManager, ConnectedTask, NoMoreTasks, NoMoreAvailableTasks


class TestTaskManager:
    task_manager: TaskManager

    def setup_method(self, method):
        """
        Before Each
        """
        self.task_manager = TaskManager(StatusManager())

    def test_connect_available_task(self):
        # Arrange
        new_task = Task(1, "", "", "")
        self.task_manager.add_new_available_task(new_task, 1234)
        connection_id = "conn_1"
        expected_connected_task = ConnectedTask(new_task, connection_id)
        # Act
        task = self.task_manager.connect_available_task(connection_id)
        # Assert
        assert new_task == task
        assert len(self.task_manager.in_progress) == 1
        assert self.task_manager.in_progress[0].task == expected_connected_task.task
        assert self.task_manager.in_progress[0].connection_id == expected_connected_task.connection_id

    def test_connect_available_task_no_tasks(self):
        # Act & Assert
        with pytest.raises(NoMoreTasks):
            assert self.task_manager.connect_available_task("")

    def test_connect_available_task_no_available_tasks(self):
        # Arrange
        connected_task = ConnectedTask(Task(1, "", None, ""), "")
        self.task_manager.in_progress.append(connected_task)
        # Act & Assert
        with pytest.raises(NoMoreAvailableTasks):
            assert self.task_manager.connect_available_task("")

    def test_connect_available_tasks_less_than_available(self):
        # Arrange
        new_task_1 = Task(1, "", "", "")
        new_task_2 = Task(2, "", "", "")
        self.task_manager.add_new_available_task(new_task_1, 1234)
        self.task_manager.add_new_available_task(new_task_2, 1234)
        connection_id = "conn_1"
        expected_connected_task_1 = ConnectedTask(new_task_1, connection_id)
        # Act
        tasks = self.task_manager.connect_available_tasks(1, connection_id)
        # Assert
        assert new_task_1 in tasks
        assert new_task_2 not in tasks
        assert len(self.task_manager.in_progress) == 1
        assert self.task_manager.in_progress[0].task == expected_connected_task_1.task
        assert self.task_manager.in_progress[0].connection_id == connection_id

    def test_connect_available_tasks(self):
        # Arrange
        new_task_1 = Task(1, "", "", "")
        new_task_2 = Task(2, "", "", "")
        self.task_manager.add_new_available_task(new_task_1, 1234)
        self.task_manager.add_new_available_task(new_task_2, 1234)
        connection_id = "conn_1"
        expected_connected_task_1 = ConnectedTask(new_task_1, connection_id)
        expected_connected_task_2 = ConnectedTask(new_task_2, connection_id)
        # Act
        tasks = self.task_manager.connect_available_tasks(3, connection_id)
        # Assert
        assert new_task_1 in tasks
        assert new_task_2 in tasks
        assert len(self.task_manager.in_progress) == 2
        assert self.task_manager.in_progress[0].task == expected_connected_task_1.task
        assert self.task_manager.in_progress[1].task == expected_connected_task_2.task
        assert self.task_manager.in_progress[0].connection_id == connection_id
        assert self.task_manager.in_progress[1].connection_id == connection_id

    def test_connect_available_tasks_no_tasks(self):
        # Act & Assert
        with pytest.raises(NoMoreTasks):
            assert self.task_manager.connect_available_tasks(5, "")

    def test_connection_dropped(self):
        # Arrange
        connection_id_1 = "connection_1"
        connection_id_2 = "connection_2"
        task_1 = Task(1, "", None, "")
        task_2 = Task(2, "", None, "")
        task_3 = Task(3, "", None, "")
        self.task_manager.add_new_available_task(task_1, 1234)
        self.task_manager.add_new_available_task(task_2, 1234)
        self.task_manager.add_new_available_task(task_3, 1234)
        self.task_manager.connect_available_tasks(2, connection_id_1)
        self.task_manager.connect_available_task(connection_id_2)
        # Act
        self.task_manager.connection_dropped(connection_id_1)
        # Assert
        assert len(self.task_manager.in_progress) == 1
        assert self.task_manager.in_progress[0].task.task_id == task_3.task_id
        assert self.task_manager.available_tasks.qsize() == 2
        assert self.task_manager.available_tasks.get().task_id == task_1.task_id
        assert self.task_manager.available_tasks.get().task_id == task_2.task_id

    def test_new_available_task(self):
        # Arrange
        new_task = Task(1, "", None, "")
        # Act
        self.task_manager.add_new_available_task(new_task, 1234)
        # Assert
        assert self.task_manager.available_tasks.qsize() == 1
        assert self.task_manager.available_tasks.get() == new_task

    def test_new_available_tasks(self):
        # Arrange
        new_tasks = [Task(1, "", None, ""), Task(2, "", None, "")]
        for task in new_tasks:
            task.job_id = 1234
        # Act
        self.task_manager.add_new_available_tasks(new_tasks, 1234)
        # Assert
        assert self.task_manager.available_tasks.qsize() == 2
        assert self.task_manager.available_tasks.get() == new_tasks[0]
        assert self.task_manager.available_tasks.get() == new_tasks[1]

    def test_task_finished_queue(self):
        # Arrange
        finished_task = Task(1, "", None, "")
        finished_task.job_id = 1234
        # Act
        self.task_manager.task_finished(finished_task)
        # Assert
        assert self.task_manager.finished_tasks.qsize() == 1
        assert self.task_manager.finished_tasks.get() == finished_task

    def test_task_finished_in_progress(self):
        # Arrange
        finished_task = Task(1, "", "", "")
        task = Task(2, "", "", "")
        self.task_manager.add_new_available_task(finished_task, 1234)
        self.task_manager.add_new_available_task(task, 1234)
        self.task_manager.connect_available_tasks(2, "")
        # Act
        self.task_manager.task_finished(finished_task)
        # Assert
        assert len(self.task_manager.in_progress) == 1
        assert self.task_manager.in_progress[0].task == task
        assert self.task_manager.finished_tasks.qsize() == 1
        assert self.task_manager.finished_tasks.get() == finished_task
        assert self.task_manager.status_manager.status.num_tasks_done == 1
        assert not self.task_manager.status_manager.is_job_done()

    def test_tasks_finished(self):
        # Arrange
        finished_tasks = [Task(1, "", None, ""), Task(2, "", None, ""), Task(3, "", None, "")]
        # Act
        self.task_manager.tasks_finished(finished_tasks)
        # Assert
        assert self.task_manager.finished_tasks.qsize() == 3
        assert self.task_manager.status_manager.status.num_tasks_done == 3
        assert self.task_manager.status_manager.is_job_done()

    def test_flush_finished_tasks(self):
        # Arrange
        tasks = [Task(1, "", None, ""), Task(2, "", None, ""), Task(3, "", None, "")]
        finished_tasks = tasks.copy()
        self.task_manager.tasks_finished(finished_tasks)
        # Act
        flushed = self.task_manager.flush_finished_tasks()
        # Assert
        assert flushed == tasks
