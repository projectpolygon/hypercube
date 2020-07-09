from os import path

from common.task import Task
from master.master import HyperMaster, JobInfo


if __name__ == "__main__":
    job: JobInfo = JobInfo()
    job.job_path = f'{path.dirname(path.abspath(__file__))}/job'
    job.file_names = ["test_file.txt"]

    master: HyperMaster = HyperMaster()
    master.init_job(job)

    cmd = "echo Hello"
    payload = 0b1010
    task1: Task = Task(1, cmd, payload, "task1.txt")

    cmd = "echo World"
    task2: Task = Task(2, cmd, payload, "task1.txt")

    master.load_tasks([task1, task2])

    master.start_server()
