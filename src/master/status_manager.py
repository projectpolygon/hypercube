"""
Contains implemented functionality for handling status changes and status logging
"""

from common.logging import Logger

logger = Logger()


class Status:
    """
    Status object for holding current master status
    """
    def __init__(self):
        self.num_slaves: int = 0
        self.num_tasks_done: int = 0
        self.num_tasks: int = 0
        self.job_done: bool = False


class StatusManager:
    """
    Manages Manager Status
    """
    log_prefix = '[StatusManager]\n'

    def __init__(self):
        self.status = Status()
        self.job_id: int = -1
        logger.log_trace(f"{self.log_prefix}Status Manager Initialized")

    def new_slave_connected(self):
        """
        Updates the status when a new slave is connected

        :return:
        """
        self.status.num_slaves += 1
        logger.log_trace(f"{self.log_prefix}Status updated.\n{self.get_status()}")

    def slave_disconnected(self):
        """
        Updates the status when a slave is disconnected

        :return:
        """
        self.status.num_slaves -= 1
        logger.log_trace(f"{self.log_prefix}Status updated.\n{self.get_status()}")

    def tasks_loaded(self, num_tasks: int):
        """
        Updates the status when tasks are loaded

        :param num_tasks:
        :return:
        """
        if num_tasks > 0:
            self.status.num_tasks = num_tasks
            logger.log_trace(f"{self.log_prefix}Status updated.\n{self.get_status()}")
        else:
            logger.log_error(f"{self.log_prefix}Number of tasks loaded must be greater than 0")
            raise ValueError

    def tasks_completed(self, num_completed: int = 1):
        """
        Updates the status when tasks have been completed

        :param num_completed:
        :return:
        """
        if num_completed > 0:
            self.status.num_tasks_done += num_completed
            logger.log_trace(f"{self.log_prefix}Status updated.\n{self.get_status()}")
        else:
            logger.log_error(f"{self.log_prefix}Number of tasks completed must be greater than 0")
            raise ValueError

    def job_completed(self):
        """
        Updates the status when the job has completed

        :return:
        """
        self.status.job_done = True
        logger.log_trace(f"{self.log_prefix}Status updated.\n{self.get_status()}")

    def is_job_done(self):
        """
        Returns True is the job is completed. False otherwise

        :return Boolean:
        """
        return self.status.job_done

    def get_status(self) -> str:
        """
        Returns a string representation of the current status

        :return String:
        """
        completion_percentage = 0.00
        if self.status.num_tasks > 0:
            completion_percentage = (self.status.num_tasks_done / self.status.num_tasks) * 100.00
        status_output = f'Job ID: {self.job_id}\n'
        status_output = f'Connected Slaves: {self.status.num_slaves}\n'
        status_output += f'Tasks Done: {self.status.num_tasks_done}\n'
        status_output += f'Total Tasks: {self.status.num_tasks}\n'
        status_output += 'Progress: {:0.2f}%\n'.format(completion_percentage)
        status_output += f'Job Completed: {self.is_job_done()}'
        return status_output

    def print_status(self):
        """
        Prints the status out in a logger

        :return:
        """
        status_printer = Logger()
        status_printer.log_success(self.get_status(), "JOB STATUS")
