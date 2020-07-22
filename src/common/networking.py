"""
implementation for common networking functions
"""

from socket import AF_INET, SOCK_DGRAM, socket, error as SocketError


def get_ip_addr():
    """
    Get own ip address

    :return Any:
    """
    sock: socket = socket(AF_INET, SOCK_DGRAM)
    try:
        # doesn't matter what to connect to, just used to get socket
        sock.connect(('8.8.8.8', 80))
        ip = sock.getsockname()[0]
    except SocketError:
        # if socket failed to get socket name, use localhost
        ip = '127.0.0.1'
    finally:
        sock.close()
    return ip
