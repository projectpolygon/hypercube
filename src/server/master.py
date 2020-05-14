import threading
import socketserver
import socket
from src.server.message import Message, MessageType
from pickle import dumps as to_bytes

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
        client_address = str(self.client_address)
        # Add connection to dict with client_address as key
        connections[client_address] = self.request  # self.request is the TCP socket connected to the client
        # while connection live
        msg = Message(MessageType.JOB_REQUEST, b'this is just test data in bytes, blah blah boop de boop bleep blap')

        while 1:
            # currently just waiting for message, then sending back howdy
            data = self.request.recv(1024)
            if not data:
                continue
            data = data.strip()
            print(client_address + " -> ", data)
            self.request.send(to_bytes(msg))
        # Remove connection from dict after disconnect
        connections[client_address] = None


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Class extends TCPServer with Threading capabilities
    """
    pass


if __name__ == "__main__":
    HOST, PORT = get_ip_addr(), 9999

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
