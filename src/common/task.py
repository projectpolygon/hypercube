from enum import Enum


class TaskMessageType(Enum):
    TASK_RAW = 0
    TASK_PROCESSED = 1
    TASK_END = 2


class Task:
    id: int
    job_id: int
    message_type: TaskMessageType
    cmd: str
    payload: bytes
    result_filename: str

    def __init__(self, task_id: int, cmd: str, payload, result_filename: str):
        self.id = task_id
        self.cmd = cmd
        self.payload = payload
        self.result_filename = result_filename

    def __eq__(self, other):
        """
        Needed to make an instance of this object comparable
        """
        if not isinstance(other, type(self)):
            raise ValueError(f"Object is of type {type(other)}. Expected type {type(self)}")
        return self.id == other.id and self.job_id == other.job_id

    def set_job(self, job_id: int):
        self.job_id = job_id

    def set_message_type(self, message_type: TaskMessageType):
        self.message_type = message_type
