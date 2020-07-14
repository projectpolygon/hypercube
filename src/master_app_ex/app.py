"""
An example app that imports master and prepares the tasks
"""

from os import path

from common.task import Task
from master.master import HyperMaster, JobInfo


if __name__ == "__main__":
    job: JobInfo = JobInfo()
    job.job_path = f'{path.dirname(path.abspath(__file__))}/job'
    job.file_names = ["test_file.txt"]

    master: HyperMaster = HyperMaster()
    master.init_job(job)

    CMD = "echo Hello"
    PAYLOAD = 0b1010
    task1: Task = Task(1, CMD, PAYLOAD, "task1.txt")

    CMD = "echo World"
    task2: Task = Task(2, CMD, PAYLOAD, "task1.txt")

    master.load_tasks([task1, task2])

    master.start_server()
