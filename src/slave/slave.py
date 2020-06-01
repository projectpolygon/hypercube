import sys
from requests import Session, cookies, ConnectionError
import shlex
from pathlib import Path
from shutil import rmtree
from subprocess import run
from time import sleep
from zlib import decompress, error as DecompressException
from random import random
from common.networking import get_ip_addr
from common.api.types import MasterInfo
import common.api.endpoints as endpoints


class HyperSlave():
    """
    When the slave is started, this class should be what the user application
    can import to begin using the features of the system on the slave itself
    """

    def __init__(self, PORT=5678):
        self.session: Session = None
        self.IP_ADDR = None
        self.HOST = None
        self.PORT = PORT
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
                
                except ValueError:
                    print('INFO: Master provided no info')

                return session

        except ConnectionError:
            return None

        except Exception as e:
            # allows breaking out of the loop
            if e == KeyboardInterrupt:
                print('Keyboard Interrupt detected. Exiting...')
                exit(0)
            else:
                print('ERR:', e)
                exit(1)
                
        return None

    def attempt_master_connection(self, master_port):
        """
        Attempt to find and connect to the master node
        """
        self.IP_ADDR = get_ip_addr()
        network_id = self.IP_ADDR.rpartition('.')[0]
        print('INFO: attempting master connection')
        for i in range(0, 255):
            hostname = network_id + "." + str(i)
            session = self.connect(hostname, master_port)
            if session is not None:
                self.set_session(session)
                print("\rINFO: master found at: ",
                      hostname + ':' + str(master_port))
                return hostname
            else:
                print("\rINFO: master not at: ", hostname +
                      ':' + str(master_port), end='')
        return None

    def set_session(self, session: Session):
        session_id = self.IP_ADDR + '-' + str(random() * random() * 123456789)
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
        except OSError as e:
            print("ERR:", e)
            return
        print("INFO: Saved.")

    def get_file(self, file_name):
        """
        Requests a file from the master.
        Returns a success boolean
        """
        print("INFO: requesting file: {}".format(file_name))
        resp = self.session.get(f'http://{self.HOST}:{self.PORT}/{endpoints.FILE}/{self.job_id}/{file_name}')
        if not resp:
            print("ERR: file was not returned")
            return False

        print("INFO: File: {} recieved. Saving now...".format(file_name))

        try:
            file_data = decompress(resp.content)
        except DecompressException as e:
            print('Err:', e)
            return False

        self.save_processed_data(file_name, file_data)
        return True

    def req_job(self):
        """
        Connection established, request a job
        """

        resp = self.session.get(
            f'http://{self.HOST}:{self.PORT}/{endpoints.JOB}', timeout=5)

        # return if there is no job
        if not resp:
            return

        # parse as JSON
        try:
            job_json = resp.json()
            self.job_id: int = job_json.get("job_id")
            job_file_names: list = job_json.get("file_names")
        except:
            print("ERR: job data JSON not received. Cannot continue")
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
        try:
            resp = self.session.get(
                url=f'http://{self.HOST}:{self.PORT}/{endpoints.HEARTBEAT}', timeout=1)

            if resp.status_code == 200:
                return True
            else:
                print("ERR: Connection is not healthy")

        except ConnectionError:
            print("ERR: Master cannot be reached.")

        except Exception as e:
            print("ERR:", e)
        
        return False

    def start(self):
        """
        Poll network for job server (master)
        """
        self.HOST = None
        while self.HOST is None:
            self.HOST = self.attempt_master_connection(self.PORT)
            if self.HOST is not None:
                break
            print('\nINFO: Retrying...',)
            sleep(1)
        print("INFO: Connection Successful")
        self.req_job()

    def run_shell_command(self, command):
        """
        Execute a shell command outputing stdout/stderr to a result.txt file.
        Returns the shell commands returncode.
        """
        args = shlex.split(command)

        with open('ApplicationResultLog.txt', "w") as f:
            output = run(args, stdout=f, stderr=f, text=True)

        return output.returncode


if __name__ == "__main__":
    master_port = 5678
    if len(sys.argv) == 2:
        master_port = sys.argv[1]
    while True:
        try:
            client: HyperSlave = HyperSlave(master_port)
            client.start()
        except KeyboardInterrupt as e:
            print("\nINFO: graceful shutdown...")
            break
