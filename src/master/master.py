import threading
from time import sleep
import socketserver
import socket
from common.message import Message, MessageType
from common.networking import *
from pickle import dumps as to_bytes, loads as from_bytes
from pathlib import Path

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
	def job_request(self):
		slave_address = str(self.client_address)

		data = self.request.recv(1024)

		if not data:
			return None

		if slave_message.meta_data.message_type is not MessageType.JOB_REQUEST:
			return None

		print("Client", client_address, ": JOB_REQUEST")

		# depickle the object
		slave_message: Message = from_bytes(data)
		return slave_message
	
	def send_job(self):
		# Create JOB DATA message
		# holds the actual job informatioun
		job_msg = Message(MessageType.JOB_DATA, job_data)
		data = to_bytes(job_msg)
		size = len(data)

		# Create JOB SYNC message and send
		sync_msg = Message(MessageType.JOB_SYNC)
		sync_msg.meta_data.job_id = int('1234')
		sync_msg.meta_data.size = size
		connection.sendall(to_bytes(sync_msg))

		# Send JOB DATA message
		print('Sending job message (' + str(size) + ' bytes)')
		total_sent = 0
		while total_sent < size:
			sent = connection.send(data[total_sent:])
			if sent == 0:
				continue
			total_sent = total_sent + sent

	def send_file(self, message: Message):
		if message.meta_data.message_type is not MessageType.FILE_REQUEST:
			return None
		print(message.payload)
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
		# JOB_REQUEST comes in
		print("new request")
		slave_message: Message = self.job_request()
		if not slave_message:
			return

		# Add connection to dict with client_address as key
		# self.request is the TCP socket connected to the client
		connection: socket.socket = self.request
		connections[client_address]: socket.socket = connection

		# perform SYNC and DATA for job
		self.send_job()

		# while connection live, allow file and task synchronization
		while True:
			# wait for job_sync from client, indicating job is done
			data = connection.recv(1024)
			if not data:
				continue
			slave_msg: Message = from_bytes(data)

			self.send_file(slave_msg)
			self.send_task(slave_msg)

			print("Message", client_address, "->", client_msg.get_data())

		# Remove connection from dict after disconnect
		connections[client_address] = None


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Class extends TCPServer with Threading capabilities
    """
    pass


def get_job():
    while True:
        if not Path('./job').exists():
            sleep(1)
            continue
        print('Job Found, Reading data...')
        with open('./job', 'rb') as job:
            data = job.read()
            print('Job uncompressed size:', len(data))
            return data


if __name__ == "__main__":
	print("1) fetching job file")	
	job_data = get_job()

	HOST, PORT = get_ip_addr(), 9999
	print(HOST + ':' + str(PORT))
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
			running = server_thread.is_alive()
			server.server_close()

