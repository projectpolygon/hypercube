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
    """
	
	def send_job(self):
		# Create JOB DATA message
		connection : socket.socket = self.request	
		job_msg : Message = job_object.get_message()

		# Encode JOB_DATA as bytes
		job_msg_bytes = to_bytes(job_msg)
		job_msg_len = len(job_msg_bytes)

		# Send the JOB_SYNC message
		sync_message: Message = Message(MessageType.JOB_SYNC)
		sync_message.meta_data.job_id = job_msg.meta_data.job_id
		sync_message.meta_data.size = job_msg_len
		connection.sendall(to_bytes(sync_message))

		# Receive the JOB_SYNC response
		sync_response : Message = from_bytes(connection.recv(1024))
		if sync_response.meta_data.message_type != MessageType.JOB_SYNC:
			return

		print("INFO: connection synchronized")

		# Send the JOB_DATA
		connection.sendall(job_msg_bytes)

	def send_file(self, message: Message):
		connection : socket.socket = self.request

		# FILE_REQUEST
		if message.meta_data.message_type is not MessageType.FILE_REQUEST:
			print(message.meta_data.message_type)
			return False
		try:
			print("INFO: sending file: {}".format(message.files[0]))
			with open(message.files[0], 'rb') as requested_file:
				requested_file_data = requested_file.read()

				# Create FILE_DATA
				data_msg: Message = Message(MessageType.FILE_DATA, requested_file_data)
				data_msg.job_id = job_object.job_id
				data_msg_bytes = to_bytes(data_msg)

				# Create FILE_SYNC
				sync_msg:Message = Message(MessageType.FILE_SYNC)
				sync_msg.meta_data.size = len(data_msg_bytes)

				# Send FILE_SYNC
				connection.sendall(to_bytes(sync_msg))

				# Recieve FILE_SYNC
				sync_response: Message = from_bytes(connection.recv(1024))
				if sync_response.meta_data.message_type != MessageType.FILE_SYNC:
					return False

				connection.sendall(data_msg_bytes)
				print("INFO: sent file: {}".format(message.files[0]))
		except Exception as e:
			print(e)
			print("ERROR: file was asked for, but not found")
			return False
		
		return True

	def send_task(self, message: Message):
		"""
		Pull a task from the global queue and send it to the slave
		"""
		if message.meta_data.message_type is not MessageType.TASK_REQUEST:
			return False
		return True

	def handle(self):
		"""
		Handle each new TCP connection
		This will represent one complete session
		"""
		# JOB_REQUEST
		slave_address = str(self.client_address)

		data = self.request.recv(1024)
		if not data:
			return 

		# depickle the object
		slave_message: Message = from_bytes(data)

		if slave_message.meta_data.message_type is not MessageType.JOB_REQUEST:
			return 

		print("INFO: client", slave_address, ": connected")

		# Add connection to dict with client_address as key
		# self.request is the TCP socket connected to the client
		connections[slave_address]: socket.socket = self.request
		
		# JOB_SYNC and JOB_DATA
		self.send_job()
		print("INFO: job sent")

		# while connection live, allow file and task synchronization
		while True:
			# wait for job_sync from client, indicating job is done
			data = self.request.recv(1024)
			if not data:
				continue
			slave_msg: Message = from_bytes(data)

			# handle FILE_REQUEST
			status = self.send_file(slave_msg)
			if not status:
				break

			# handle TASK_REQUEST
			status = self.send_task(slave_msg)
			if not status:
				break

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
				print("INFO: jobfile size (uncmp): {}".format(len(data)))
				job = Job()
				job.load_from_bytes(data)
				return job
		except Exception as e:
			print(e)
			print("ERROR: jobfile not found")

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("ERROR: expected 2 arguments")
		sys.exit()
	
	# load the jobfile and wrap it in an object that we can manipulate	
	job_object : Job = get_job()
	HOST, PORT = get_ip_addr(), 9999

	# speeds up debugging when a port is in use
	ThreadedTCPServer.allow_reuse_address = True
	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	with server:
		# each connection handled in its own thread
		server_thread = threading.Thread(target=server.serve_forever)
		# Exit the server thread when the main thread terminates
		server_thread.daemon = True
		server_thread.start()
		print("INFO: server running in thread:", server_thread.name)
		running = server_thread.is_alive()
		while running:
			try:
				running = server_thread.is_alive()
			except KeyboardInterrupt:
				print("\nINFO: Graceful shutdown...")
				break
		server.shutdown()
		server.server_close()
	print("INFO: job complete")

