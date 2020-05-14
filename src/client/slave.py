import socket
import time
from message import Message, MessageType
from pickle import dumps as to_bytes, loads as from_bytes

def get_ip_addr():
    """
    Get own ip address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))  # doesn't matter what to connect to, just used to get socket
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
            return sock
        else:
            print("Master not at: ", hostname)
            sock.close()
    return None


def process_job(connection: socket.socket, job_size: int):
    processed = 0
    data = None
    while processed < job_size:
        msg: Message = from_bytes(connection.recv(1024))
        data = data + msg.get_data()
        processed += msg.meta_data.size
    return data


if __name__ == "__main__":
    connection: socket.socket = None
    while connection is None:
        connection = attempt_master_connection(9999)
        time.sleep(1)

    # Connection established
    # Create Job Request Message and send
    msg = Message(MessageType.JOB_REQUEST)
    connection.sendall(to_bytes(msg))
    response: Message = from_bytes(connection.recv(1024))

    if response.meta_data.message_type is MessageType.JOB_SYNC:
        # processed_data = process_job(connection, response.meta_data.size)
        processed_data = response.get_data()

    print("Processed data: {}".format(processed_data))

    connection.sendall(to_bytes(Message(MessageType.JOB_SYNC, processed_data)))
    connection.close()
