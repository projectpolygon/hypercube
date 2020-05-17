import threading
from time import sleep
import socketserver
import socket
from common.message import Message, MessageType
from common.networking import *
from common.job import *
from pickle import dumps as to_bytes, loads as from_bytes
from pathlib import Path
import sys

# dict to keep track of live connections
connections = {}

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
	"""
    Handler created for each connection.
    Connection is closed when function returns

    1) JOB REQUEST from slave
    	- message from slave requesting job file

	2) JOB_SYNC from master
		- sends the job file METADATA to the slave

	3) JOB_DATA from master
		- send the job file ITSELF
		- slave now knows the names of files it needs

	4) FILE_REQUEST from slave (can happen as many time as required)
		- request file from master

	5) FILE_SYNC from master
		- get info about the file size
	
	6) FILE_DATA from master
		- actual file contents
	.
	.
	.

	5) TASK_REQUEST from slave
		- ask for a task_file
	6) TASK_SYNC from master
		- message containing task JSON size
	7) TASK_DATA from master
		- actual task data
	8) TASK_SYNC from slave
		- contains the image size
	9) TASK_DATA from slave
		- contain the image itself
	.
	.
	.
	Final TASK_REQUEST
	slave will receive JOB_END message
	
	
    """
	
	def send_job(self):
		connection : socket.socket = self.request	
		# Create JOB DATA message
		#job_msg : Message = Message(MessageType.JOB_DATA, job_data)
		job_msg = job_object.get_message()
		size = 0
		if job_msg.payload:
			size = len(job_msg.payload)
		data = job_msg.payload
		#data = to_bytes(job_object)i

		# Create JOB SYNC message and send
		#sync_msg = Message(MessageType.JOB_SYNC)
		#sync_msg.meta_data.job_id = '1234'
		#sync_msg.meta_data.size = size
		#sync_msg.payload = ["test1.txt", "test2.txt"]
		connection.sendall(to_bytes(job_msg))

		# Send JOB DATA message
		print('Sending job message (' + str(size) + ' bytes)')
		total_sent = 0
		while total_sent < size:
			sent = connection.send(data[total_sent:])
			if sent == 0:
				continue
			total_sent = total_sent + sent

	def send_file(self, message: Message):
		connection : socket.socket = self.request	
		if message.meta_data.message_type is not MessageType.FILE_REQUEST:
			print(message.meta_data.message_type)
			return None
		try:
			print("Searching for {}".format(message.files[0]))
			with open(message.files[0], 'rb') as reqfile:
				reqdata = reqfile.read()

				data_msg:Message = Message(MessageType.FILE_DATA, reqdata)
				data_msg.job_id = job_object.job_id
				sync_msg:Message = Message(MessageType.FILE_SYNC)
				sync_msg.payload_size = len(reqdata)

				connection.sendall(to_bytes(sync_msg))
				print("Sent SYNC")
				sleep(2)

				connection.sendall(to_bytes(data_msg))
				print("Sent DATA")
		except Exception as e:
			print(e)
			print("CRIT ERR: file was asked for, but not found")
		#with file_to_send as open("r", message.payload):
		
		# parse message for filename
		# open file
		# read contents
		# get filesize
		# send filesize in SYNC message
		# send file itself
	
	def send_task(self, message: Message):
		if message.meta_data.message_type is not MessageType.TASK_REQUEST:
			return None
		# poll the global queue for a task
		# if there is a task, SYNC the taskfile size
			# then, send TASK FILE
		# if there is no task, AND ALL JOBS ARE DONE END_JOB

#		pass
#	def file_sync(self):
#		pass
#	def file_data(self):
#		pass
#	
#	def task_request(self):
#		pass
#	def task_sync(self):
#		pass
#	def task_data(self):
#		pass

	def handle(self):
		"""
		Handle each new TCP connection
		This will represent one complete session
		"""
		# JOB_REQUEST comes in
		# slave_address, slave_message: Message = self.job_request()
		# if not slave_message:
		# return
		slave_address = str(self.client_address)

		data = self.request.recv(1024)
		if not data:
			return 

		# depickle the object
		slave_message: Message = from_bytes(data)

		if slave_message.meta_data.message_type is not MessageType.JOB_REQUEST:
			return 

		print("Client", slave_address, ": JOB_REQUEST")

		# Add connection to dict with client_address as key
		# self.request is the TCP socket connected to the client
		connections[slave_address]: socket.socket = self.request
		
		# perform SYNC and DATA for job
		self.send_job()
		print("Job Sent")

		# while connection live, allow file and task synchronization
		while True:
			# from this point on, the only message types to be expected
			# are as follow:
			# FILE_REQUEST
			# TASK_REQUEST
			# TASK_SYNC
			# TASK_DATA
			# wait for job_sync from client, indicating job is done
			data = self.request.recv(1024)
			if not data:
				continue
			slave_msg: Message = from_bytes(data)

			self.send_file(slave_msg)
			self.send_task(slave_msg)

			print("Message", slave_address, "->", slave_msg.get_data())

		# Remove connection from dict after disconnect
		connections[slave_address] = None


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Class extends TCPServer with Threading capabilities
    """
    pass


def get_job():
	while True:
		try:
			with open(sys.argv[1], 'rb') as jobfile:
				data = jobfile.read()
				print("INF: jobfile size (uncmp): {}".format(len(data)))
				job = Job()
				job.load_from_bytes(data)
				return job
		except Exception as e:
			print(e)
			print("ERR: jobfile not found")

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("ERROR: expected 2 arguments")
		sys.exit()
	
	# load the jobfile
	job_object : Job = get_job()
	HOST, PORT = get_ip_addr(), 9999

	# speeds up debugging when a port is in use
	ThreadedTCPServer.allow_reuse_address = True
	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	with server:
		# Start a thread with the server -- that thread will then start
		# another thread for each request
		server_thread = threading.Thread(target=server.serve_forever)
		# Exit the server thread when the main thread terminates
		server_thread.daemon = True
		server_thread.start()
		print("Server loop running in thread:", server_thread.name)
		running = server_thread.is_alive()
		while running:
			try:
				running = server_thread.is_alive()
			except KeyboardInterrupt:
				print("\nGraceful shutdown...")
				break
		server.shutdown()
		server.server_close()

