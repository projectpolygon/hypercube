import socket
import time

'''
Get own ip address
'''
def get_ip_addr():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80)) # doesn't matter what to connect to, just used to get socket
        IP = s.getsockname()[0]
    except:
        # if socket failed to get sockname, use localhost
        IP = '127.0.0.1' 
    finally:
        s.close()
    return IP

'''
Connect to a hostname on given post
'''
def connect(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(0.05)
    result = sock.connect_ex((hostname, port))
    return sock, (result == 0)

'''
Attempt to find and connect to the master node
'''
def attempt_master_connection(master_port):
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
    sock = None
    while(sock == None):
        sock = attempt_master_connection(9999)
        time.sleep(1)

    # Connection established
    # Just sending Hello, waiting for a response, and then closing connection
    sock.sendall(bytes('Hello', 'ascii'))
    response = str(sock.recv(1024), 'ascii')
    print("Received: {}".format(response))
    sock.close()