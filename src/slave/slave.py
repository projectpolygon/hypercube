"""
Implemented fuctionality to run a slave node for a distributed workload
"""

# External imports
from json import loads as json_loads
from pathlib import Path
from random import random
from shlex import split as cmd_split
from shutil import rmtree
from pickle import dumps as pickle_dumps, loads as pickle_loads, PicklingError, UnpicklingError
from subprocess import CalledProcessError, run
from sys import argv, exit as sys_exit
from time import sleep
from typing import List
from zlib import compress, decompress, error as CompressionException
from requests import Session, cookies, exceptions as RequestExceptions
from os import path

# Internal imports
import common.api.endpoints as endpoints
from common.api.types import MasterInfo
from common.logging import Logger
from common.networking import get_ip_addr
from .heartbeat import Heartbeat
from common.task import Task, TaskMessageType

logger = Logger()


class HyperSlave:
    """
    When the slave is started, this class should be what the user application
    can import to begin using the features of the system on the slave itself
    """

    def __init__(self, port=5678):
        self.heartbeat = None
        self.session: Session = None
        self.ip_addr = None
        self.host = None
        self.port = port
        self.job_id = None
        self.job_path = None
        self.master_info: MasterInfo = None
        self.running = False

    def init_job_root(self):
        """
        Initializes the job root directory
        """

        cwd = str(Path.cwd().resolve())
        job_root_dir_path = cwd + '/job'
        Path.mkdir(Path(job_root_dir_path), parents=True, exist_ok=True)
        self.job_path = job_root_dir_path

    def connect(self, hostname, port):
        """
        Connect to a hostname on given post
        """
        session: Session = Session()
        try:
            # try for a response within 0.075s
            resp = session.get(
                f'http://{hostname}:{port}/{endpoints.DISCOVERY}', timeout=0.075)
            # 200 okay returned, master discovery succeeded
            if resp.status_code == 200:
                try:
                    self.master_info = resp.json()
                    return session

                except ValueError:
                    logger.log_error('Master provided no info')

        except (ConnectionError, RequestExceptions.ConnectionError):
            return None

        # allows breaking out of the loop
        except KeyboardInterrupt:
            logger.log_debug('Keyboard Interrupt detected. Exiting...')
            sys_exit(0)

        except Exception as error:
            logger.log_error(
                f'Exception of type {type(error)} occurred\n{error}')
            sys_exit(1)

        return None

    def attempt_master_connection(self, master_port):
        """
        Attempt to find and connect to the master node
        """

        self.ip_addr = get_ip_addr()
        network_id = self.ip_addr.rpartition('.')[0]
        logger.log_info('Attempting master connection')
        for i in range(0, 256):
            hostname = network_id + "." + str(i)
            session = self.connect(hostname, master_port)
            if session is not None:
                self.set_session(session)
                logger.log_success(
                    f"Connected to {hostname}:{master_port}", "MASTER CONNECTED")
                return hostname
            logger.print_sameline(f'Master not at: {hostname}:{master_port}')
        return None

    def set_session(self, session: Session):
        """
        Setup the session through the use of a cookie
        Cookie is created with a unique session id
        """

        session_id = self.ip_addr + '-' + str(random() * random() * 123456789)
        cookie = cookies.create_cookie('id', session_id)
        session.cookies.set_cookie(cookie)
        self.session = session

    def create_job_dir(self):
        """
        Create job directory based on job id
        Overwrites the directory if it exists
        """

        path = f'{self.job_path}/{self.job_id}'
        rmtree(path=path, ignore_errors=True)
        Path(path).mkdir(parents=True, exist_ok=False)
        return path

    def save_processed_data(self, file_name, file_data):
        """
        Write job bytes to file
        """
        try:
            with open(f'{self.job_path}/{self.job_id}/{file_name}', 'wb') as new_file:
                new_file.write(file_data)
        except OSError as error:
            logger.log_error(f'{error}')
            return
        logger.log_success('Processed data saved')

    def get_file(self, file_name):
        """
        Requests a file from the master.
        Returns a success boolean
        """
        logger.log_info(f'requesting file: {file_name}')
        resp = self.session.get(
            f'http://{self.host}:{self.port}/{endpoints.FILE}/{self.job_id}/{file_name}'
        )
        if not resp:
            logger.log_error(f'File: {file_name} was not returned')
            return False

        logger.log_info(f'File: {file_name} received. Saving now...')

        try:
            file_data = decompress(resp.content)
        except CompressionException as error:
            logger.log_error(f'{error}')
            return False

        self.save_processed_data(file_name, file_data)
        return True

    def req_job(self):
        """
        Connection established, request a job
        """

        logger.log_info(f'Request made to {endpoints.JOB}')
        resp = self.session.get(
            f'http://{self.host}:{self.port}/{endpoints.JOB}', timeout=5)

        if not resp:
            logger.log_info(f'Request made to {endpoints.JOB} was not returned')
            return

        # parse as JSON
        try:
            job_json = json_loads(resp.json())
            self.job_id: int = job_json.get("job_id")
            job_file_names: list = job_json.get("file_names")

        except ValueError:
            logger.log_error('Job data JSON not received. Cannot continue')
            return

        except Exception as error:
            logger.log_error(f'{error}')
            return

        # create a working directory
        self.create_job_dir()

        # FILE_REQUEST for each file in JOB_DATA list of file names
        for file_name in job_file_names:
            self.get_file(file_name)

        status = self.handle_tasks()
        if not status:
            logger.log_error("Failed to handle tasks")
        elif status == TaskMessageType.TASK_END:
            logger.log_info("No more tasks to run")
        else:
            logger.log_error("Unknown exit status when handling error")

    def req_tasks(self):
        """
        Requests a task from the master node, if task failed to receive try up to 5 times
        TODO: make this request tasks for as many cpu cores as it has using multiprocessings cpu_count()
        """
        max_tasks = 1

        for i in range(5):
            logger.log_info(f'Request made to {endpoints.GET_TASKS}')

            # parse JSON
            try:
                resp = self.session.get(
                    f'http://{self.host}:{self.port}/{endpoints.GET_TASKS}/{self.job_id}/{max_tasks}', timeout=5)
                tasks: List[Task] = pickle_loads(decompress(resp.data))
                return tasks

            except CompressionException as error:
                logger.log_error(f'Unable to decompress raw data\n{error}')
                return
            except UnpicklingError as error:
                logger.log_error(f'Unable to unpickle decompressed tasks\n{error}')
                return
            except Exception:
                logger.log_error('Task data JSON not received, trying again.')
                if i < 4:
                    continue
                else:
                    logger.log_error('Task data JSON not received after 5 attempts, cannot continue.')
                    return

    def execute_tasks(self, tasks):
        """
        Executes the received tasks
        TODO: make these tasks run using multiprocessing instead of subprocess.run()
        """
        for task in tasks:
            task_file = 'task_' + str(task.id)
            command = task.command + ' ' + task_file
            status = run_shell_command(command, task_file)
            if status != 0:
                # TODO: add either retry step or send back failed results to master to be executed on  a different node
                logger.log_error(task_file + " failed to execute correctly")
            elif status == 0:
                logger.log_info(task_file + " executed correctly")
        return

    def start(self):
        """
        Initializes job root directory,
        polls network for job server (master),
        then requests a job from the master
        """
        self.init_job_root()

        self.host = None
        while self.host is None:
            self.host = self.attempt_master_connection(self.port)
            if self.host is not None:
                break
            logger.log_info("Retrying...")
            sleep(1)
        self.heartbeat = Heartbeat(
            session=self.session, url=f'http://{self.host}:{self.port}/{endpoints.HEARTBEAT}')
        self.heartbeat.start_beating()
        self.req_job()

    def handle_tasks(self):
        """
        Main loop to handle the tasks until the job is completed or the slave disconnects
        """
        while True:
            # Get some tasks from master
            received_tasks = self.req_tasks()
            completed_tasks = []
            # if failed to receive tasks after 5 attempts it cannot continue
            if not received_tasks:
                logger.log_warn('No tasks received. Wait 20 seconds then try again')
                sleep(20)
                continue
            elif received_tasks[0].message_type == TaskMessageType.TASK_END:
                return TaskMessageType.TASK_END
            else:
                # For each task make a file containing the the task content
                try:
                    for task in received_tasks:
                        task_file = "task_" + str(task.task_id)
                        self.save_processed_data(task_file, task.payload)
                        logger.log_info('Creating ' + task_file + ' file to use during execution')

                    self.execute_tasks(received_tasks)

                    for task in received_tasks:
                        if path.exists(f'{self.job_path}/{self.job_id}/{task_file}'):
                            Path(f'{self.job_path}/{self.job_id}/{task_file}').unlink()
                            logger.log_info('Removing ' + task_file + ' file when no longer needed')

                        with open(task.result_filename, 'r') as file:
                            result = file.read()

                        current_task: Task = Task(task.task_id, task.cmd, result, task.result_filename)
                        current_task.message_type = TaskMessageType.TASK_PROCESSED
                        current_task.job_id = self.job_id
                        completed_tasks.append(current_task)

                    pickled_tasks = pickle_dumps(completed_tasks)
                    compressed_data = compress(pickled_tasks)
                    response = self.session.post(f'/{endpoints.TASKS_DONE}/{self.job_id}', data=compressed_data)

                    if response is 200:
                        logger.log_info('Completed tasks sent back to master successfully')
                    else:
                        logger.log_error(
                            'Completed tasks failed to send back to master successfully, error response: ' + str(
                                response))
                except PicklingError as error:
                    logger.log_error(f'Unable to pickle tasks\n{error}')
                    return
                except CompressionException as error:
                    logger.log_error(f'Unable to compress pickled tasks\n{error}')
                    return
                except FileNotFoundError as error:
                    logger.log_error(f'Unable to find {self.job_path}/{self.job_id}/{task_file} specified\n{error}')
                    return
                except Exception as error:
                    logger.log_error(f'{error}')
                    return


def run_shell_command(command, task_id):
    """
    Execute a shell command outputing stdout/stderr to a result.txt file.
    Returns the shell commands returncode.
    """
    args = cmd_split(command)

    try:
        with open('ApplicationResultLog.txt', "w") as result_file:
            print('Task_' + task_id + ':"', file=result_file)
            output = run(args, stdout=result_file,
                         stderr=result_file, text=True, check=True)
            print('"', file=result_file)

        return output.returncode

    except CalledProcessError as error:
        logger.log_error(error.output.decode('utf-8'))


if __name__ == "__main__":
    MASTER_PORT = 5678
    if len(argv) == 2:
        MASTER_PORT = int(argv[1])
    elif len(argv) > 2:
        logger.log_error('Too many arguments given')
        sys_exit(1)
    while True:
        try:
            client: HyperSlave = HyperSlave(MASTER_PORT)
            client.start()
        except KeyboardInterrupt:
            logger.log_debug('Graceful shutdown...')
            break
