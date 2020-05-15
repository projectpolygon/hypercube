import threading
from time import sleep
import socketserver
import socket
from sys import getsizeof
from message import Message, MessageType
from pickle import dumps as to_bytes, loads as from_bytes
from pathlib import Path

# dict to keep track of live connections
connections = {}


def get_ip_addr():
    """
    Get own ip address
    """
    s: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))  # doesn't matter what to connect to, just used to get socket
        ip = s.getsockname()[0]
    except socket.error:
        # if socket failed to get sockname, use localhost
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    Handler created for each connection.
    Connection is closed when function returns
    """

    def handle(self):

        #  job
        client_address = str(self.client_address)
        data = self.request.recv(1024)
        if not data:
            return
            
        client_message: Message = from_bytes(data)
        if client_message.meta_data.message_type is not MessageType.JOB_REQUEST:
            return
        
        print("Client", client_address, ": JOB_REQUEST")
        # Add connection to dict with client_address as key
        connection: socket.socket = self.request # self.request is the TCP socket connected to the client
        connections[client_address]: socket.socket = connection
        
        # Create JOB DATA message
        job_msg = Message(MessageType.JOB_DATA, job_data)
        data = to_bytes(job_msg)
        size = getsizeof(data)

        # Create JOB SYNC message and send
        sync_msg = Message(MessageType.JOB_SYNC)
        sync_msg.meta_data.job_id = '0'
        sync_msg.meta_data.size = size
        connection.sendall(to_bytes(sync_msg))
        
        # Send JOB DATA message
        print('Sending job message (' + str(size) + ' bytes)')
        total_sent = 0
        while total_sent < size - 33:
            sent = connection.send(data[total_sent:])
            if sent == 0:
                continue

            total_sent = total_sent + sent
            print(total_sent)

        # while connection live
        while 1:
            # wait for job_sync from client, indicating job is done
            data = connection.recv(1024)
            if not data:
                break
            client_msg: Message = from_bytes(data)
            if client_msg.meta_data.message_type is not MessageType.JOB_SYNC:
                continue

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
        if not Path('./thanos.png').exists():
            sleep(1)
            continue
        print('Job Found, Reading data...')
        with open('./thanos.png', 'rb') as job:
            data = job.read()
            print('Job uncompressed size:', str(getsizeof(data)))
            return data


if __name__ == "__main__":
    job_data = get_job()

    HOST, PORT = get_ip_addr(), 1234

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
