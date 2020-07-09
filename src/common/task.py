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

    def __init__(self, task_id: int, cmd: str, payload):
        self.task_id = task_id
        self.cmd = cmd
        self.payload = payload

    def set_job(self, job_id: int):
        self.job_id = job_id

    def set_message_type(self, message_type: TaskMessageType):
        self.message_type = message_type

    def set_result_filename(self, result_filename: str):
        self.result_filename = result_filename
