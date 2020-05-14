import socket
import time
from src.client.message import Message, MessageType
from pickle import loads as from_bytes

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
    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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


if __name__ == "__main__":
    connection: socket = None
    while connection is None:
        connection = attempt_master_connection(9999)
        time.sleep(1)

    # Connection established
    # Just sending Hello, waiting for a response, and then closing connection
    connection.sendall(bytes('Hello', 'ascii'))
    response: Message = from_bytes(connection.recv(1024))
    print("Received: {}".format(response.get_data()))
    connection.close()
