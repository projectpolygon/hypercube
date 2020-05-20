import socket
from time import sleep
from common.message import Message, MessageType
from common.networking import *
from pickle import dumps as to_bytes, loads as from_bytes
from pathlib import Path
from shutil import rmtree

def connect(hostname, port):
	"""
	Connect to a hostname on given post
	"""
	sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket.setdefaulttimeout(0.05)
	result = sock.connect_ex((hostname, port))
	return sock, (result == 0)

def attempt_master_connection(master_port):
	"""
	Attempt to find and connect to the master node
	"""
	network_id = get_ip_addr().rpartition('.')[0]
	print('') # print down a line so we dont overwrite something else
	for i in range(0, 255):
		hostname = network_id + "." + str(i)
		sock, connected = connect(hostname, master_port)
		if connected:
			print("\rINFO: master found at: ", hostname + ':' + str(master_port))
			sock.settimeout(None)
			return sock, hostname
		else:
			print("\rINFO: master not at: ", hostname + ':' + str(master_port), end='')
			sock.close()
	return None, None

#TODO this should be the method we use to transfer all files, we should rename it to something more representative
def process_job(connection: socket.socket, job_size: int):
    """
    Recieve data from server and unpack it
    """
    chunks = []
    bytes_recieved = 0
    while bytes_recieved < job_size:
        bytes_left = job_size - bytes_recieved
        chunk = connection.recv(min(bytes_left, 2048))
        if chunk == b'':
            print("WARNING: connection lost... reconnecting")
            connected = False
            # recreate socket
            sock = socket.socket()
            while not connected:
                # attempt to reconnect, otherwise sleep for 2 seconds
                try:
                    sock.connect((HOST, PORT))
                    connected = True
                    print("INFO: re-connection successful")
                except socket.error:
                    sleep(2)

        chunks.append(chunk)
        bytes_recieved = bytes_recieved + len(chunk)
    data_recieved = b''.join(chunks)
    msg: Message = from_bytes(data_recieved)
    return msg
	#data = msg.get_data()
    #print('Finished Processing Job')
    #return data

class slave_client():
	"""
	When the slave is started, this class should be what the user application
	can import to begin using the features of the system on the slave itself
	"""
	def __init__(self):
		self.running = False
	
	def create_job_dir(self, job_id):
		"""
		Create job directory based on job id
		Overwrites the directory if it exists
		"""
		path = "./job" + str(job_id)
		rmtree(path=path, ignore_errors=True)
		Path(path).mkdir(parents=True, exist_ok=False)
		return path

	def save_processed_data(self, job_id, data):
		"""
		Write job bytes to file
		"""
		path = create_job_dir(job_id) + "/job"
		with open(path, "wb") as out_file:
			out_file.write(data)
	
	def file_get(self, filename, connection):
		print("INFO: requesting file: {}".format(filename))
		file_request = Message(MessageType.FILE_REQUEST)
		file_request.files = [filename]

		# Send FILE_REQUEST
		connection.sendall(to_bytes(file_request))

		# Receive FILE_SYNC
		file_sync : Message = from_bytes(connection.recv(1024))
		expected_bytes = file_sync.meta_data.size
		if file_sync.meta_data.message_type != MessageType.FILE_SYNC:
			return

		# Send FILE_SYNC
		file_sync_response : Message = Message(MessageType.FILE_SYNC)
		connection.sendall(to_bytes(file_sync_response))

		file_data = process_job(connection, expected_bytes)
		with open("./job" + str(file_data.job_id) + "/" + filename, 'wb') as new_file:
			new_file.write(file_data.get_payload())
		
		print("INF: requested file: {} downloaded".format(filename))
		
	def start_job(self, connection):
		"""
		Connection established, handle the job
		"""
		print("INFO: connection made")
		self.running = True
		msg = Message(MessageType.JOB_REQUEST)
		connection.sendall(to_bytes(msg))		
		try:
            # receive JOB_SYNC from master
			job_sync: Message = from_bytes(connection.recv(1024))
            # TODO: error handling in case this is not enough to receive the whole sync
		except Exception as e:
			print(e)
			return
        
		# Check the message type
		if job_sync.meta_data.message_type != MessageType.JOB_SYNC:
			return
        
		# create a working directory
		self.create_job_dir(job_sync.meta_data.job_id)

        # send JOB_SYNC
		job_sync_response : Message = Message(MessageType.JOB_SYNC)
		job_sync_response.meta_data.job_id = job_sync.meta_data.job_id
		connection.sendall(to_bytes(job_sync_response))

        # receive JOB_DATA
		job_data:Message = process_job(connection, job_sync.meta_data.size)
		if job_data.meta_data.message_type != MessageType.JOB_DATA:
			return

		# FILE_REQUEST for each file in JOB_DATA list of filenames
		for job_file in job_data.job_files:
			self.file_get(job_file, connection)
			
		while True:
			# TODO handle the rest of the job
			continue

	def start(self):
		"""
		Poll network for job server (master)
		"""
		while True:
			connection: socket.socket = None
			while connection is None:
				connection, HOST = attempt_master_connection(PORT)
				sleep(1)
			self.start_job(connection)

if __name__ == "__main__":
	PORT = 9999
	client: slave_client = slave_client()
	client.start()
