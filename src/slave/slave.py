import sys
import requests
import base64
import shlex
from common.networking import *
from pathlib import Path
from shutil import rmtree
from subprocess import run
from time import sleep

def connect(hostname, port):
	"""
	Connect to a hostname on given post
	"""
	try:
		# try for a response within 0.05
		req = requests.get("http://{}:{}/HEARTBEAT".format(hostname, port), timeout=0.05)
		# 200 okay returned, heartbeat at this address succeeded
		if req.status_code == 200:
			return True
	except Exception as e:
		# allows breaking out of the loop
		if e == KeyboardInterrupt:
			throw	
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
			print("\rINFO: master found at: ", hostname + ':' + str(master_port))
			#sock.settimeout(None)
			return hostname
		else:
			print("\rINFO: master not at: ", hostname + ':' + str(master_port), end='')
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
		with open("./job" + str(self.job_id) + "/" + file_name, 'wb') as new_file:
			new_file.write(file_data)

	def file_get(self, file_name):
		print("INFO: requesting file: {}".format(file_name))
		file_request = requests.get("http://{}:{}/FILE_GET/{}/{}"
			.format(self.HOST, self.PORT, self.job_id, file_name))
		if not file_request:
			print("ERR: file was not returned")
			return False

		file_json = file_request.json()
		file_data = base64.b64decode(file_json.get("payload").encode("ascii"))	
		self.save_processed_data(file_name, file_data)
		return True
				
	def handle_job(self):
		"""
		Connection established, handle the job
		"""
		print("INFO: connection made")
		# JOB_GET
		job_request = requests.get("http://{}:{}/JOB_GET".format(self.HOST, self.PORT), timeout=5)
		
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
			self.file_get(file_name)
					
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
			self.HOST= attempt_master_connection(self.PORT)
			sleep(1)
		self.handle_job()

	def run_cpp(command):
		"""
		Execute a c++ executable and create a result file
		"""
		args = shlex.split(command)

		with open('result.txt', "w") as f:
			run(args, stdout=f, stderr=f, text=True)

if __name__ == "__main__":
	master_port=5678
	if len(sys.argv) == 2:
		master_port = sys.argv[1]
	while True:
		try:
			client: HyperSlave = HyperSlave(master_port)
			client.start()
		except KeyboardInterrupt as e:
			print("\nINFO: graceful shutdown...")
			break
