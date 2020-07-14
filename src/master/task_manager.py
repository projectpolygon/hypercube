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
    """
    A ConnectedTask is a task that is associated with a connected slave
    """
    def __init__(self, task: Task, connection_id: str):
        self.task = task
        self.connection_id = connection_id


class TaskManager:
    """
    Manages Tasks
    """

    def __init__(self):
        self.available_tasks: SimpleQueue = SimpleQueue()
        self.in_progress: List[ConnectedTask] = []
        self.finished_tasks: SimpleQueue = SimpleQueue()

    def connect_available_task(self, connection_id: str) -> Task:
        """
        Connects a task with a connection id associated with the connected slave
        Returns the task
        """
        try:
            task: Task = self.available_tasks.get(timeout=0)
            connected_task: ConnectedTask = ConnectedTask(task, connection_id)
            self.in_progress.append(connected_task)
            return task
        except Empty:
            if len(self.in_progress) == 0:
                raise NoMoreTasks
            else:
                raise NoMoreAvailableTasks

    def connect_available_tasks(self, num_tasks: int, connection_id: str) -> List[Task]:
        """
        Connects num_tasks amount of tasks with a connection id associated with the connected slave
        Returns a list of the tasks
        """
        tasks: List[Task] = []
        for i in range(num_tasks):
            try:
                tasks.append(self.connect_available_task(connection_id))
            except NoMoreAvailableTasks:
                return tasks
            except NoMoreTasks:
                raise NoMoreTasks
        return tasks

    def connection_dropped(self, connection_id: str):
        """
        Called by the master.ConnectionManager when a connection is removed.
        Removes the task from the list of In Progress Tasks
        Adds the task to the Available Tasks Queue
        """
        new_in_progress: List[ConnectedTask] = []
        for connected_task in self.in_progress:
            if connected_task.connection_id == connection_id:
                self.new_available_task(connected_task.task, connected_task.task.job_id)
            else:
                new_in_progress.append(connected_task)
        self.in_progress = new_in_progress

    def new_available_task(self, task: Task, job_id: int):
        """
        Adds the task to the Available Tasks Queue and attaches job id to them
        """
        task.set_job(job_id)
        self.available_tasks.put(task)

    def new_available_tasks(self, tasks: List[Task], job_id: int):
        """
        Adds the tasks to the Available Tasks Queue and attaches the job id to them
        """
        for task in tasks:
            self.available_tasks.put(task)

    def task_finished(self, finished_task: Task):
        """
        Removes the task from the list of In Progress Tasks
        Adds the task to the Finished Tasks Queue
        """
        self.finished_tasks.put(finished_task)
        self.in_progress = \
            [connected_task for connected_task in self.in_progress if connected_task.task.id != finished_task.id]

    def tasks_finished(self, tasks: List[Task]):
        """
        Removes the tasks from the list of In Progress Tasks
        Adds the tasks to the Finished Tasks Queue
        """
        for task in tasks:
            self.task_finished(task)

    def flush_finished_tasks(self) -> List[Task]:
        """
        Removes all tasks from the Finished Tasks Queue and returns them
        """
        tasks: List[Task] = []
        for _ in range(self.finished_tasks.qsize()):
            tasks.append(self.finished_tasks.get())
        return tasks
