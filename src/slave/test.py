# External imports
from pathlib import Path
from random import random
from shlex import split as cmd_split
from shutil import rmtree
from subprocess import CalledProcessError, run
from sys import argv, exit as sys_exit
from time import sleep
from zlib import decompress, error as DecompressException
from requests import Session, cookies

# Internal imports
import common.api.endpoints as endpoints
from common.api.types import MasterInfo
from common.logging import Logger
from common.networking import get_ip_addr

logger = Logger()


class HyperSlave():
    """
    When the slave is started, this class should be what the user application
    can import to begin using the features of the system on the slave itself
    """

    def __init__(self, PORT=5678):
        self.session: Session = None
        self.ip_addr = None
        self.host = None
        self.port = PORT
        self.job_id = None
        self.master_info: MasterInfo = None

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
                    self.master_info = MasterInfo(resp.json())
                    return session

                except ValueError:
                    logger.log_error('Master provided no info')

        except ConnectionError:
            return None

        # allows breaking out of the loop
        except KeyboardInterrupt:
            logger.log_debug('Keyboard Interrupt detected. Exiting...')
            sys_exit(0)

        except Exception as error:
            logger.log_error(error)
            sys_exit(1)

        return None

    def attempt_master_connection(self, master_port):
        """
        Attempt to find and connect to the master node
        """
        self.ip_addr = get_ip_addr()
        network_id = self.ip_addr.rpartition('.')[0]
        logger.log_info('Attempting master connection')
        for i in range(0, 255):
            hostname = network_id + "." + str(i)
            session = self.connect(hostname, master_port)
            if session is not None:
                self.set_session(session)
                logger.log_success(f"Connected to {hostname}:{master_port}", "MASTER CONNECTED")
                return hostname
        print(f'\rMaster not at: {hostname}:{master_port}', end='')
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
        path = "./job" + str(self.job_id)
        rmtree(path=path, ignore_errors=True)
        Path(path).mkdir(parents=True, exist_ok=False)
        return path

    def save_processed_data(self, file_name, file_data):
        """
        Write job bytes to file
        """
        try:
            with open("./job" + str(self.job_id) + "/" + file_name, 'wb') as new_file:
                new_file.write(file_data)
        except OSError as error:
            logger.log_error(error)
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


        logger.log_info(f'File: {file_name} recieved. Saving now...')

        try:
            file_data = decompress(resp.content)
        except DecompressException as error:
            logger.log_error(error)
            return False

        self.save_processed_data(file_name, file_data)
        return True

    def req_job(self):
        """
        Connection established, request a job
        """

        resp = self.session.get(
            f'http://{self.host}:{self.port}/{endpoints.JOB}', timeout=5)

        # return if there is no job
        if not resp:
            return

        # parse as JSON
        try:
            job_json = resp.json()
            self.job_id: int = job_json.get("job_id")
            job_file_names: list = job_json.get("file_names")
        except Exception:
            logger.log_error('Job data JSON not received. Cannot continue')
            return

        # create a working directory
        self.create_job_dir()

        # FILE_REQUEST for each file in JOB_DATA list of filenames
        for file_name in job_file_names:
            self.get_file(file_name)

        while True:
            # TODO handle the rest of the job
            # TASK_GET
            # TASK_DATA

            # Send Heartbeat
            self.send_heartbeat()
            sleep(1)
            continue

    def send_heartbeat(self):
        """
        Send heartbeat to the master to keep its connection with master
        """
        try:
            resp = self.session.get(
                url=f'http://{self.host}:{self.port}/{endpoints.HEARTBEAT}', timeout=1)

            if resp.status_code == 200:
                return True

            logger.log_warn(f"Connection is not healthy ({self.host}:{self.port})")

        except ConnectionError:
            logger.log_error(f"Master cannot be reached. ({self.host}:{self.port})")

        except Exception as error:
            logger.log_error(error)

        return False

    def start(self):
        """
        Poll network for job server (master)
        """
        self.host = None
        while self.host is None:
            self.host = self.attempt_master_connection(self.port)
            if self.host is not None:
                break
            logger.log_info("Retrying...")
            sleep(1)
        self.req_job()

def run_shell_command(command):
    """
    Execute a shell command outputing stdout/stderr to a result.txt file.
    Returns the shell commands returncode.
    """
    args = cmd_split(command)

    try:
        with open('ApplicationResultLog.txt', "w") as result_file:
            output = run(args, stdout=result_file, stderr=result_file, text=True, check=True)

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
