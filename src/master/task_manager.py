from queue import SimpleQueue, Empty
from typing import List

from common.task import Task
from common.logging import Logger

logger = Logger()


class NoMoreTasks(Exception):
    """
    Exception raised when there are no more tasks available or in progress
    """


class NoMoreAvailableTasks(Exception):
    """
    Exception raised when there are no more tasks available
    """


class ConnectedTask:
    def __init__(self, task: Task, connection_id: str):
        self.task = task
        self.connection_id = connection_id


class TaskManager:
    available_tasks: SimpleQueue = SimpleQueue()
    in_progress: List[ConnectedTask]
    finished_tasks: SimpleQueue = SimpleQueue()

    def connect_available_task(self, connection_id: str):
        try:
            task: Task = self.available_tasks.get()
            connected_task: ConnectedTask = ConnectedTask(task, connection_id)
            self.in_progress.append(connected_task)
            return task
        except Empty:
            if len(self.in_progress) == 0:
                raise NoMoreTasks
            else:
                raise NoMoreAvailableTasks

    def connect_available_tasks(self, num_tasks: int, connection_id: str):
        tasks: List[Task] = []
        for i in range(num_tasks):
            try:
                tasks.append(self.connect_available_task(connection_id))
            except NoMoreAvailableTasks:
                return tasks
            except NoMoreTasks:
                raise NoMoreTasks

    def connection_dropped(self, connection_id: str):
        pass
        # new_in_progress: List[Task] = []
        # for task in self.in_progress:
            # if task.connection_id == connection_id:


    def new_available_task(self, task: Task):
        self.available_tasks.put(task)

    def task_finished(self, finished_task: Task):
        self.finished_tasks.put(finished_task)
        self.in_progress = \
            [connected_task for connected_task in self.in_progress if connected_task.task.id != finished_task.id]

    def tasks_finished(self, tasks: List[Task]):
        for task in tasks:
            self.task_finished(task)
