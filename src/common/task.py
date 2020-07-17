"""
The Task Object is passed between the master and slave.
"""

from enum import Enum


class TaskMessageType(Enum):
    """
    Enum for the types a Task Message can be
    """
    TASK_RAW = 0
    TASK_PROCESSED = 1
    TASK_END = 2


class Task:
    """
    A object that contains the expected parameters for a task used by the master and slave
    The cmd and the payload are passed to the slave application
    """
    task_id: int
    job_id: int
    message_type: TaskMessageType
    cmd: str
    payload: bytes
    result_filename: str

    def __init__(self, task_id: int, cmd: str, payload, result_filename: str):
        self.task_id = task_id
        self.cmd = cmd
        self.payload = payload
        self.result_filename = result_filename

    def __eq__(self, other):
        """
        Needed to make an instance of this object comparable
        """
        if not isinstance(other, type(self)):
            raise ValueError(f"Object is of type {type(other)}. Expected type {type(self)}")
        return self.task_id == other.task_id and self.job_id == other.job_id

    def set_job(self, job_id: int):
        """
        Assigns the task a job id
        """
        self.job_id = job_id

    def set_message_type(self, message_type: TaskMessageType):
        """
        Sets the message type of the Task
        """
        self.message_type = message_type
