"""
An example app that imports master and prepares the tasks
"""

from os import path
from sys import exit as sys_exit
from threading import Thread
from time import sleep
from typing import List

from common.task import Task
from master.master import HyperMaster, JobInfo


if __name__ == "__main__":
    # Step 1: Initialise HyperMaster
    master: HyperMaster = HyperMaster()

    # Step 2: Initialise Job
    job: JobInfo = JobInfo()
    job.job_path = f'{path.dirname(path.abspath(__file__))}/job'
    job.file_names = ["test_file.txt"]
    master.init_job(job)

    # Step 3: Setup Tasks
    CMD = "echo Hello"
    PAYLOAD = 0b1010
    task1: Task = Task(1, CMD, PAYLOAD, "task1.txt")

    CMD = "echo World"
    task2: Task = Task(2, CMD, PAYLOAD, "task1.txt")

    # Step 4: Load Tasks
    master.load_tasks([task1, task2])

    # Step 5: Start Master Server
    master_thread = Thread(name='hypermaster_server_thread', target=master.start_server)
    master_thread.setDaemon(True)
    master_thread.start()

    try:
        # Step 6: Wait for job to be completed
        while not master.is_job_done():
            master.print_status()
            sleep(10)

        # Step 7: Reassemble completed tasks
        completed_tasks: List[Task] = master.get_completed_tasks()
        for task in completed_tasks:
            print(task.payload)
        sys_exit(0)

    except KeyboardInterrupt:
        # call master.exit
        print("exiting")
        sys_exit(0)
