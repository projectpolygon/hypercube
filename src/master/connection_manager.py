"""
Contains implemented functionality for handling connections between the master and slave nodes
"""

# External imports
from threading import Timer, Event

# Internal imports
from common.logging import Logger
from master.status_manager import StatusManager
from master.task_manager import TaskManager

logger = Logger()


class ConnectionDead(Exception):
    """
    Exception raised when the connection has timed out
    """


class Connection:
    """
    Connection object
    """
    log_prefix = "[Connection]\n"

    def __init__(self, connection_id: str, timeout_secs: float = 5.0):
        self.connection_id: str = connection_id
        self.timeout_secs: float = timeout_secs
        self.dead: Event = Event()
        self.timer: Timer = Timer(timeout_secs, self.timeout)
        self.timer.daemon = True
        self.timer.start()

    def __hash__(self):
        """
        Needed to make an instance of this object comparable

        :return Integer:
        """
        return hash(self.connection_id)

    def __eq__(self, other):
        """
        Needed to make an instance of this object comparable

        :param other:
        :return String:
        """
        if not isinstance(other, type(self)):
            raise ValueError(f"Object is of type {type(other)}. Expected type {type(self)}")
        return self.connection_id == other.connection_id

    def reset_timer(self):
        """
        Resets the timer for the connection

        :return:
        """
        if self.is_alive():
            self.timer.cancel()
            self.timer = Timer(self.timeout_secs, self.timeout)
            self.timer.daemon = True
            self.timer.start()
        else:
            raise ConnectionDead

    def timeout(self):
        """
        Called when the set amount of timeout seconds has been reached
        without a reset. This sets the dead flag of the connection

        :return:
        """
        logger.log_warn(f'{self.log_prefix}Connection [{self.connection_id}]: timed out')
        self.dead.set()

    def is_alive(self):
        """
        Returns True if the connection is alive, False if dead

        :return Boolean:
        """
        return not self.dead.is_set()


class ConnectionManager:
    """
    ConnectionManager object
    Manages active connections
    """
    log_prefix = "[ConnectionManager]\n"

    def __init__(self, task_manager: TaskManager,
                 status_manager: StatusManager, cleanup_timeout_secs=3.0):
        self.task_manager = task_manager
        self.status_manager = status_manager
        self.running = True
        self.connections = {}
        self.connections_cleanup_timeout = cleanup_timeout_secs
        self.connections_cleanup_timer = Timer(
            self.connections_cleanup_timeout, self.cleanup_connections)
        self.connections_cleanup_timer.daemon = True
        self.connections_cleanup_timer.start()
        logger.log_trace(f'{self.log_prefix}Connection Manager Initialized')

    def cleanup_connections(self):
        """
        Called when the connections_cleanup_timer times out.
        Removes dead connections from the connections dict
        and resets the connections_cleanup_timer

        :return:
        """
        active_connections = {}
        for connection_id, connection in self.connections.items():
            if connection.is_alive():
                active_connections[connection_id] = connection
            else:
                self.task_manager.connection_dropped(connection_id)
                self.status_manager.slave_disconnected()
                logger.log_trace(f'{self.log_prefix}Connection [{connection_id}]: removed')
        self.connections = active_connections

        if self.running:
            # Reset timer
            self.connections_cleanup_timer = Timer(
                self.connections_cleanup_timeout, self.cleanup_connections)
            self.connections_cleanup_timer.start()

    def add_connection(self, connection_id: str, timeout_secs: float = 10.0):
        """
        Adds a new connection to the connections dict
        Will replace existing connection if one exists with the same connection id

        :param connection_id:
        :param timeout_secs:
        :return:
        """
        connection: Connection = Connection(connection_id, timeout_secs)
        self.connections[connection_id] = connection
        self.status_manager.new_slave_connected()
        logger.log_success(f'{self.log_prefix}Connection [{connection_id}] Added', 'NEW CONNECTION')

    def reset_connection_timer(self, connection_id: str):
        """
        Resets a connection's timer

        :param connection_id:
        :return:
        """
        try:
            connection: Connection = self.connections.get(connection_id)
            if connection:
                connection.reset_timer()
                logger.log_trace(f'{self.log_prefix}Connection [{connection_id}] reset')
            else:
                logger.log_warn(f'{self.log_prefix}Connection [{connection_id}] not found.')
        except Exception as error:
            logger.log_error(f"{self.log_prefix}\n{error}")

    def get_connection(self, connection_id: str):
        """
        Returns an alive connection if one is found`
        else, raises ConnectionDead exception

        :param connection_id:
        :return Connection:
        """
        connection: Connection = self.connections.get(connection_id)
        if connection and connection.is_alive():
            return connection

        raise ConnectionDead
