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
    timeout_secs: float = None
    timer: Timer = None
    dead: Event = None
    connection_id: str = None

    def __init__(self, connection_id, timeout_secs=5.0):
        self.connection_id = connection_id
        self.timeout_secs = timeout_secs
        self.dead = Event()
        self.timer = Timer(timeout_secs, self.timeout)
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
