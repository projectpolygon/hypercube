"""
Heartbeat thread
"""

# External imports
from threading import Timer
from requests import Session, exceptions as RequestExceptions

# Internal imports
from common.logging import Logger

logger = Logger()


class Heartbeat:
    """
    Heartbeat Class.
    Handles sending heartbeat messages periodically
    """
    def __init__(self, session: Session, url, interval_secs: float = 2.0, retry_attempts=5):
        self.session = session
        self.url = url
        self.interval: float = interval_secs
        self.timer: Timer = Timer(self.interval, self.send_beat)
        self.fails = 0
        self.retry_attempts = retry_attempts

    def start_beating(self):
        """
        Initializes and starts the timer as a daemon thread
        """
        self.timer: Timer = Timer(self.interval, self.send_beat)
        self.timer.daemon = True
        self.timer.start()

    def reset_timer(self):
        """
        Resets the timer by cancelling and starting it
        """
        self.timer.cancel()
        self.start_beating()

    def send_beat(self):
        """
        Called when the set interval seconds has been reached

        Send heartbeat to the master to keep its connection with master
        """
        try:
            resp = self.session.get(url=f'{self.url}', timeout=1)

            if resp.status_code == 200:
                logger.log_trace(f'Heartbeat sent.\nurl: {self.url}')
                self.fails = 0

            else:
                logger.log_warn("Connection is not healthy")
                self.fails += 1

        except (RequestExceptions.ConnectionError, ConnectionError):
            logger.log_warn(
                f"Master cannot be reached. url({self.url})")
            self.fails += 1

        except Exception as error:
            logger.log_error(f'Unknown Error: {error}')
            self.fails += 1

        if self.fails >= self.retry_attempts:
            logger.log_error("Unhealthy Connection: Terminating heartbeats")
            self.stop_beating()
        else:
            self.reset_timer()

    def stop_beating(self):
        """
        Ends the timer by cancelling it
        """
        logger.log_info("Heartbeat stopped")
        self.timer.cancel()
