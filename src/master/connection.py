from time import time
from threading import Timer, Event


class ConnectionDead(Exception):
    """
    Exception raised when the connection has timed out
    """
    pass


class Connection:
    """
    Connection object 
    """

    def __init__(self, connection_id, timeout_secs=5.0):
        self.connection_id: str = connection_id
        self.timeout_secs: float = timeout_secs
        self.dead: Event = Event()
        self.timer: Timer = Timer(timeout_secs, self.timeout)
        self.timer.daemon = True
        self.timer.start()

    def __hash__(self):
        """
        Needed to make an instance of this object comparable
        """
        return hash((self.connection_id))

    def __eq__(self, other):
        """
        Needed to make an instance of this object comparable
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.connection_id == other.connection_id

    def reset_timer(self):
        """
        Resets the timer for the connection
        """
        if(self.is_alive()):
            self.timer.cancel()
            self.timer = Timer(self.timeout_secs, self.timeout)
            self.timer.start()
        else:
            raise ConnectionDead

    def timeout(self):
        """
        Called when the set ammount of timeout seconds has been reached
        without a reset. This sets the dead flag of the connection  
        """
        print(f'INFO: Connection [{self.connection_id}]: timed out')
        self.dead.set()

    def is_alive(self):
        """
        Returns True if the connection is alive, False if dead
        """
        return not self.dead.is_set()


class ConnectionManager:
    """
    ConnectionManager object
    Manages active connections 
    """

    def __init__(self):
        self.running = True
        self.connections = {}
        self.connections_cleanup_timeout = 3.0
        self.connections_cleanup_timer = Timer(
            self.connections_cleanup_timeout, self.cleanup_connections)
        self.connections_cleanup_timer.daemon = True
        self.connections_cleanup_timer.start()

    def cleanup_connections(self):
        """
        Called when the connections_cleanup_timer times out.
        Removes dead connections from the connections dict
        and resets the connections_cleanup_timer
        """
        active_connections = {}
        for connection_id, connection in self.connections.items():
            if connection.is_alive():
                active_connections[connection_id] = connection
            else:
                print(f'INFO: Connection [{connection_id}]: removed')
        self.connections = active_connections

        if(self.running):
            # Reset timer
            self.connections_cleanup_timer = Timer(
                self.connections_cleanup_timeout, self.cleanup_connections)
            self.connections_cleanup_timer.start()

    def add_connection(self, connection_id: str, timeout_secs: float = 5.0):
        """
        Adds a new connection to the connections dict
        Will replace existing connection if one exists with the same connection id
        """
        connection: Connection = Connection(connection_id, timeout_secs)
        self.connections[connection_id] = connection

    def reset_connection_timer(self, conn_id):
        """
        Resets a connection's timer
        """
        connection: Connection = self.connections.get(conn_id)
        connection.reset_timer()

    def get_connection(self, connection_id: str):
        """
        Returns an alive connection if one is found
        else, raises ConnectionDead exception
        """
        connection: Connection = self.connections.get(connection_id)
        if connection and connection.is_alive():
            return connection
        else:
            raise ConnectionDead
