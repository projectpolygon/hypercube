import sys
import requests
import shlex
from pathlib import Path
from shutil import rmtree
from subprocess import run
from time import sleep
from zlib import decompress, error as DecompressException
from common.networking import get_ip_addr
import common.api.endpoints as endpoints 


def connect(hostname, port):
    """
    Connect to a hostname on given post
    """
    try:
        # try for a response within 0.05
        req = requests.get(
            "http://{}:{}/{}".format(hostname, port, endpoints.DISCOVERY), timeout=0.05)
        # 200 okay returned, master discovery succeeded
        if req.status_code == 200:
            # TODO: discovery may return json on master information
            return True
    except Exception as e:
        # allows breaking out of the loop
        if e == KeyboardInterrupt:
            print('Keyboard Interrupt detected. Exiting...')
            exit(0)
        else:
            print('ERR:', e)
            exit(1)
    return False


def attempt_master_connection(master_port):
    """
    Attempt to find and connect to the master node
    """
    network_id = get_ip_addr().rpartition('.')[0]
    print('INFO: attempting master connection')
    for i in range(0, 255):
        hostname = network_id + "." + str(i)
        connected = connect(hostname, master_port)
        if connected:
            print("\rINFO: master found at: ",
                  hostname + ':' + str(master_port))
            return hostname
        else:
            print("\rINFO: master not at: ", hostname +
                  ':' + str(master_port), end='')
    return None


class HyperSlave():
    """
    When the slave is started, this class should be what the user application
    can import to begin using the features of the system on the slave itself
    """

    def __init__(self, PORT=5678):
        self.HOST = ""
        self.PORT = PORT
        self.job_id = 0

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
        file_request = requests.get("http://{}:{}/{}/{}/{}"
                                    .format(self.HOST, self.PORT, endpoints.FILE, self.job_id, file_name))
        if not file_request:
            print("ERR: file was not returned")
            return False

        print("INFO: File: {} recieved. Saving now...".format(file_name))

        try:
            file_data = decompress(file_request.content)
        except DecompressException as e:
            print('Err:', e)
            return False

        self.save_processed_data(file_name, file_data)
        return True

    def handle_job(self):
        """
        Connection established, handle the job
        """
        print("INFO: connection made")
        # JOB_GET
        job_request = requests.get(
            "http://{}:{}/{}}".format(self.HOST, self.PORT, endpoints.JOB), timeout=5)

        # don't continue we have no job
        if not job_request:
            return

        # parse as JSON
        try:
            job_json = job_request.json()
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
            sleep(1)
            continue

    def start(self):
        """
        Poll network for job server (master)
        """
        self.HOST = None
        while self.HOST is None:
            self.HOST = attempt_master_connection(self.PORT)
            sleep(1)
        self.handle_job()

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
