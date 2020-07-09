from common.task import Task
from master.master import HyperMaster, JobInfo

job: JobInfo
job.file_names = ["test_file.txt"]

master: HyperMaster = HyperMaster()
master.init_job(job)

cmd = "echo Hello"
payload = 0b1010
task1: Task = Task(1, cmd, payload)

cmd = "echo World"
task2: Task = Task(2, cmd, payload)

master.load_tasks([task1, task2])

master.start_server()
