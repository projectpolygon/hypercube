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

DATA = "We're no strangers to love You know the rules and so do I A full commitment's what I'm thinking of You " \
       "wouldn't get this from any other guy I just wanna tell you how I'm feeling Gotta make you understand Never " \
       "gonna give you up Never gonna let you down Never gonna run around and desert you Never gonna make you cry " \
       "Never gonna say goodbye Never gonna tell a lie and hurt you We've known each other for so long Your heart's " \
       "been aching but you're too shy to say it Inside we both know what's been going on We know the game and we're " \
       "gonna play it And if you ask me how I'm feeling Don't tell me you're too blind to see Never gonna give you up " \
       "Never gonna let you down Never gonna run around and desert you Never gonna make you cry Never gonna say " \
       "goodbye Never gonna tell a lie and hurt you Never gonna give you up Never gonna let you down Never gonna run " \
       "around and desert you Never gonna make you cry Never gonna say goodbye Never gonna tell a lie and hurt you " \
       "Never gonna give, never gonna give (Give you up) (Ooh) Never gonna give, never gonna give (Give you up) We've " \
       "known each other for so long Your heart's been aching but you're too shy to say it Inside we both know what's " \
       "been going on We know the game and we're gonna play it I just wanna tell you how I'm feeling Gotta make you " \
       "understand Never gonna give you up Never gonna let you down Never gonna run around and desert you Never gonna " \
       "make you cry Never gonna say goodbye Never gonna tell a lie and hurt you Never gonna give you up Never gonna " \
       "let you down Never gonna run around and desert you Never gonna make you cry Never gonna say goodbye Never " \
       "gonna tell a lie and hurt you Never gonna give you up Never gonna let you down Never gonna run around and " \
       "desert you Never gonna make you cry "

words = DATA.split(' ')
if __name__ == "__main__":
    # Step 1: Initialise HyperMaster
    master: HyperMaster = HyperMaster()

    # Step 2: Initialise Job
    job: JobInfo = JobInfo()
    job.job_path = f'{path.dirname(path.abspath(__file__))}/job'
    job.file_names = ["test_file.txt"]
    master.init_job(job)

    # Step 3: Setup Tasks
    tasks: List[Task] = []
    for i, word in enumerate(words):
        PROGRAM = "./slave_app_ex.sh"
        payload_file_name = f'payload_{i}.txt'
        result_file_name = f'output_{i}.txt'
        ARGS = [payload_file_name, result_file_name]
        PAYLOAD = str.encode(word)
        tasks.append(Task(i, PROGRAM, ARGS, PAYLOAD, result_file_name, payload_file_name))

    # Step 4: Load Tasks
    master.load_tasks(tasks)

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
        completed_tasks.sort(key=lambda t: t.task_id)
        for task in completed_tasks:
            print(task.payload.decode())
        sys_exit(0)

    except KeyboardInterrupt:
        # call master.exit
        print("exiting")
        sys_exit(0)
