"""
The Task Object is passed between the master and slave.
"""

from enum import Enum
from typing import List


class TaskMessageType(Enum):
    """
    Enum for the types a Task Message can be
    """
    TASK_RAW = 0
    TASK_PROCESSED = 1
    JOB_END = 2
    TASK_FAILED = 3


class Task:
    """
    A object that contains the expected parameters for a task used by the master and slave
    The cmd and the payload are passed to the slave application
    """
    task_id: int
    job_id: int
    message_type: TaskMessageType
    program: str
    arg_file_names: List[str]
    payload: bytes
    result_filename: str
    payload_filename: str

    def __init__(self, task_id: int, program: str, arg_file_names: List[str],
                 payload, result_filename: str, payload_filename: str):
        self.task_id = task_id
        self.program = program
        self.arg_file_names = arg_file_names
        self.payload = payload
        self.result_filename = result_filename
        self.payload_filename = payload_filename

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
