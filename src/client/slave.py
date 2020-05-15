import socket
from time import sleep
from message import Message, MessageType
from pickle import dumps as to_bytes, loads as from_bytes
from pathlib import Path
from shutil import rmtree


def get_ip_addr():
    """
    Get own ip address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't matter what to connect to, just used to get socket
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except socket.error:
        # if socket failed to get sockname, use localhost
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


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
            print("Master not at: ", hostname)
            sock.close()
    return None, None


def create_job_dir(job_id):
    """
    Create job directory based on job id
    Overwrites the directory if it exists
    """
    path = "./job" + str(job_id)
    rmtree(path=path, ignore_errors=True)
    Path(path).mkdir(parents=True, exist_ok=False)
    print('Created Job Dir', path)
    return path


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
    data = msg.get_data()
    print('Finished Processing Job')
    return data


def save_processed_data(job_id, data):
    """
    Write job bytes to file
    """
    path = create_job_dir(job_id) + "/job"
    with open(path, "wb") as out_file:
        print('Writing data to file:', path)
        out_file.write(data)


if __name__ == "__main__":
    PORT = 9999
    connection: socket.socket = None
    while connection is None:
        connection, HOST = attempt_master_connection(PORT)
        sleep(1)

    # Connection established
    # Create Job Request Message and send
    msg = Message(MessageType.JOB_REQUEST)
    connection.sendall(to_bytes(msg))
    response: Message = from_bytes(connection.recv(1024))

    # wait for job sync message
    while response.meta_data.message_type is not MessageType.JOB_SYNC:
        continue

    processed_data = process_job(connection, response.meta_data.size)

    if processed_data is not None:
        save_processed_data(response.meta_data.job_id, processed_data)

    connection.sendall(
        to_bytes(Message(MessageType.JOB_SYNC, b'Finished Processing, goodbye')))
    connection.close()
