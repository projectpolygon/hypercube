import threading
import socketserver
import socket

# dict to keep track of live connections
connections = {}

def get_ip_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

'''
Handler created for each connection. 
Connection is closed when function returns
'''
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_address = str(self.client_address)
        # Add connection to dict with client_address as key
        connections[client_address] = self.request # self.request is the TCP socket connected to the client
        # while connection live
        while 1:
            # currectly just waiting for message, then sending back howdy
            self.data = self.request.recv(1024)
            if not self.data:
                continue
            self.data = self.data.strip()
            print(client_address + " -> ", self.data)
            self.request.send(b'howdy')
        # Remove connection from dict after disconnect
        connections[client_address] = None

'''
Class extends TCPServer with Threading capabilities
'''
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
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
        while(running):
            running = server_thread.is_alive()
        server.server_close()
