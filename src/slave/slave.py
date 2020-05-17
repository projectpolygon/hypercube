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
    for i in range(0, 255):
        hostname = network_id + "." + str(i)
        sock, connected = connect(hostname, master_port)
        if connected:
            print("Master found at: ", hostname + ':' + str(master_port))
            sock.settimeout(None)
            return sock, hostname
        else:
            print("Master not at: ", hostname + ':' + str(master_port))
            sock.close()
    return None, None

def process_job(connection: socket.socket, job_size: int):
    """
    Recieve data from server and unpack it
    """
    chunks = []
    bytes_recieved = 0
    while bytes_recieved < job_size:
        print(bytes_recieved)
        bytes_left = job_size - bytes_recieved
        # TODO the chunking can't just rely on the payload. 
        # Since the object must be account for as well!!!!
        chunk = connection.recv(min(bytes_left + 1000, 2048)) # NOTICE THE + 1000
        if chunk == b'':
            print("connection lost... reconnecting")
            connected = False
            # recreate socket
            sock = socket.socket()
            while not connected:
                # attempt to reconnect, otherwise sleep for 2 seconds
                try:
                    sock.connect((HOST, PORT))
                    connected = True
                    print("re-connection successful")
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


def save_processed_data(job_id, data):
    """
    Write job bytes to file
    """
    path = create_job_dir(job_id) + "/job"
    with open(path, "wb") as out_file:
        print('Writing data to file:', path)
        out_file.write(data)

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
		print('Created Job Dir', path)
		return path
	
	def file_get(self, filename, connection):
		print("Asking for file: {}".format(filename))
		msg = Message(MessageType.FILE_REQUEST)
		msg.files = [filename]

		# send the FILE_REQUEST message
		connection.sendall(to_bytes(msg))
		sleep(1)

		# TODO: This may fail if the file isnt found!!!!
		sync_response:Message = from_bytes(connection.recv(1024))

		# parse the payload as an int
		expected:int = int(sync_response.payload_size)
		print("expecting file of size {}".format(expected))

		data = process_job(connection, expected)
		print(data.test())
		with open("./job" + str(data.job_id) + "/" + filename, 'wb') as new_file:
			new_file.write(data.get_data())
		# wait to receive the FILE_SYNC message

	def start_job(self, connection):
		"""
		Connection established, handle the job
		"""
		print("Connection found")
		self.running = True
		msg = Message(MessageType.JOB_REQUEST)
		connection.sendall(to_bytes(msg))		
		try:
			response: Message = from_bytes(connection.recv(1024))
		except Exception as e:
			print(e)
			return

		# create a working directory
		self.create_job_dir(response.meta_data.job_id)

		# fetch each required job file
		for job_file in response.job_files:
			self.file_get(job_file, connection)
		print(response.meta_data.job_id)
		print(response.meta_data.message_type)
		print(response.payload)
		print(response.job_files)
		while True:
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
   

    # Connection established
    # Create Job Request Message and send
    #msg = Message(MessageType.JOB_REQUEST)
    #connection.sendall(to_bytes(msg))
    #response: Message = from_bytes(connection.recv(1024))

    # wait for job sync message
    #while response.meta_data.message_type is not MessageType.JOB_SYNC:
    #    continue

    #processed_data = process_job(connection, response.meta_data.size)

    #if processed_data is not None:
    #    save_processed_data(response.meta_data.job_id, processed_data)

    #connection.sendall(
    #    to_bytes(Message(MessageType.JOB_SYNC, b'Finished Processing, goodbye')))
    #connection.close()
