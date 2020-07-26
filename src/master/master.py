"""
Implemented functionality to run a master node for a distributed workload
"""

# External imports
from io import BytesIO
from json import dumps as json_dumps
from math import ceil
from os import makedirs
from pathlib import Path
from pickle import dumps as pickle_dumps, loads as pickle_loads, PicklingError, UnpicklingError
from random import random
from sys import exit as sys_exit
from typing import List
from zlib import compress, decompress, error as CompressionException
from flask import Flask, Response, jsonify, request, send_file

# Internal imports
import common.api.endpoints as endpoints
from common.api.types import MasterInfo
from common.logging import Logger
from common.networking import get_ip_addr
from common.task import Task, TaskMessageType
from .status_manager import StatusManager
from .connection_manager import ConnectionManager
from .task_manager import TaskManager, NoMoreTasks, NoMoreAvailableTasks

logger = Logger()


class JobInfo:
    """
    Object that defines a job
    Meant to be imported and set by app that imports master
    """
    job_id: int
    job_path: str
    file_names: List[str]
    user_opts = None


class JobNotInitialized(AttributeError):
    """
    Exception raised when a operation requires the job to be initialized
    but it isn't
    """


class WrongJob(Exception):
    """
    Exception raised when an endpoint's job id is not associated to this
    master's current job
    """


class HyperMaster:
    """
    HyperMaster Class.
    """

    def __init__(self, host="0.0.0.0", port=5678):
        self.host = host
        self.port = port
        self.test_config = None
        self.status_manager = StatusManager()
        self.task_manager = TaskManager(self.status_manager)
        self.conn_manager: ConnectionManager = \
            ConnectionManager(self.task_manager, self.status_manager)
        self.job: JobInfo = JobInfo()

    def load_tasks(self, tasks: List[Task]):
        """
        Loads tasks into the Task Manager
        Meant to be used by app that imports master to load prepared tasks

        :param tasks:
        :return:
        """
        if not hasattr(self.job, 'job_id'):
            logger.log_error("Can't load tasks for uninitialized job")
            raise JobNotInitialized

        self.task_manager.add_new_available_tasks(tasks, self.job.job_id)
        self.status_manager.tasks_loaded(len(tasks))

    def init_job(self, job: JobInfo):
        """
        Initializes the job for the master.
        Ensures job files exist

        :param job:
        :return:
        """

        for file_name in job.file_names:
            if not Path(f'{job.job_path}/{file_name}').exists():
                logger.log_error(
                    f'{file_name} not found in job folder. Cannot continue')
                sys_exit(1)

        self.job = job
        self.job.job_id = ceil(random() * random() * 9999)
        self.status_manager.job_id = self.job.job_id
        logger.log_success(f'Job {self.job.job_id} initialized ')

    def start_server(self):
        """
        Starts the server

        :return:
        """
        app = create_app(self)
        app.run(host=self.host, port=self.port, debug=True, use_reloader=False)

    def create_routes(self, app):
        """
        Creates the required routes

        :param app:
        :return Any:
        """

        def job_check(job_id: int):
            if not hasattr(self.job, 'job_id'):
                logger.log_error("Uninitialized Job")
                raise JobNotInitialized
            if job_id != self.job.job_id:
                logger.log_warn('Slave contacting wrong master')
                raise WrongJob

        def create_binary_resp(data: bytes, file_name: str):
            return send_file(
                BytesIO(data),
                mimetype='application/octet-stream',
                as_attachment=True,
                attachment_filename=file_name
            )

        @app.route(f'/{endpoints.JOB}')
        # pylint: disable=W0612
        def get_job():
            """
            Endpoint to handle job request from the slave

            :return Any:
            """
            if self.is_job_done():
                return Response(status=404)

            conn_id = request.cookies.get('id')

            logger.log_info(
                f'Job request from {conn_id},\nSaving connection...')
            self.conn_manager.add_connection(conn_id)

            # read and parse the JSON
            job_json = json_dumps(self.job, default=lambda o: o.__dict__, sort_keys=True)
            return jsonify(job_json)

        @app.route(f'/{endpoints.FILE}/<int:job_id>/<string:file_name>', methods=["GET"])
        # pylint: disable=W0612
        def get_file(job_id: int, file_name: str):
            """
            Endpoint to handle file request from the slave

            :param job_id:
            :param file_name:
            :return Any:
            """
            try:
                job_check(job_id)
                with open(f'{self.job.job_path}/{file_name}', "rb") as file:
                    file_data = file.read()
                    compressed_data = compress(file_data)
                    logger.log_info(
                        f'Sending {file_name} as part of job {job_id}')
                    return create_binary_resp(compressed_data, file_name)

            except JobNotInitialized:
                return Response(response="Job Not Initialized", status=403)

            except WrongJob:
                return Response(response="Wrong Master", status=403)

            except CompressionException as error:
                logger.log_error(f'Unable to compress file data\n{error}')
                return Response(status=500)

            except FileNotFoundError as error:
                logger.log_error(f'Unable to find \'{file_name}\'\n{error}')
                return Response(status=404)

            except Exception as error:
                logger.log_error(f'{type(error)} {error}')
                return Response(status=501)

        @app.route(f'/{endpoints.GET_TASKS}/<int:job_id>/<int:num_tasks>', methods=["GET"])
        # pylint: disable=W0612
        def get_tasks(job_id: int, num_tasks: int):
            """
            fetch task from the queue
            return this task "formatted" back to slave

            :param job_id: Integer
            :param num_tasks: Integer
            :return Any:
            """
            try:
                conn_id = request.cookies.get('id')
                job_check(job_id)
                tasks: List[Task] = self.task_manager.connect_available_tasks(num_tasks, conn_id)
                pickled_tasks = pickle_dumps(tasks)
                compressed_data = compress(pickled_tasks)
                return create_binary_resp(compressed_data, f'tasks_job_{self.job.job_id}')

            except NoMoreAvailableTasks:
                return Response(status=42)

            except NoMoreTasks:
                if self.status_manager.is_job_done():
                    job_finished_task = Task(-1, "", [], None, "", "")
                    job_finished_task.set_message_type(TaskMessageType.JOB_END)
                    pickled_tasks = pickle_dumps([job_finished_task])
                    compressed_data = compress(pickled_tasks)
                    return create_binary_resp(compressed_data, f'job_{self.job.job_id}_done')

                logger.log_error('Unable to retrieve tasks from manager')
                return Response(status=500)

            except JobNotInitialized:
                return Response(response="Job Not Initialized", status=403)

            except WrongJob:
                return Response(response="Wrong Master", status=403)

            except PicklingError as error:
                logger.log_error(f'Unable to pickle tasks\n{error}')
                return Response(status=500)

            except CompressionException as error:
                logger.log_error(f'Unable to compress pickled tasks\n{error}')
                return Response(status=500)

            except Exception as error:
                logger.log_error(f'{type(error)} {error}')
                return Response(status=501)

        @app.route(f'/{endpoints.TASKS_DONE}/<int:job_id>', methods=["POST"])
        # pylint: disable=W0612
        def tasks_done(job_id: int):
            """
            arguments: job_id: int
            Gets completed task  and pass payload to application
            return 200 ok

            :param job_id:
            :return Response:
            """
            try:
                job_check(job_id)
                raw_data = request.get_data()
                tasks: List[Task] = pickle_loads(decompress(raw_data))
                self.task_manager.tasks_finished(tasks)
                return Response(status=200)

            except JobNotInitialized:
                return Response(response="Job Not Initialized", status=403)

            except WrongJob:
                return Response(response="Wrong Master", status=403)

            except CompressionException as error:
                logger.log_error(f'Unable to decompress raw data\n{error}')
                return Response(status=500)

            except UnpicklingError as error:
                logger.log_error(f'Unable to unpickle decompressed tasks\n{error}')
                return Response(status=500)

            except Exception as error:
                logger.log_error(f'{type(error)} {error}')
                return Response(status=501)

        @app.route(f'/{endpoints.DISCOVERY}')
        # pylint: disable=W0612
        def discovery():
            """
            Endpoint used for initial master discovery for the slave.
            Returns master information in json format to slave

            :return Any:
            """
            master_info: MasterInfo = {
                "ip": get_ip_addr()
            }
            return jsonify(master_info)

        @app.route(f'/{endpoints.HEARTBEAT}')
        # pylint: disable=W0612
        def heartbeat():
            """
            Heartbeat received from a slave, indicating it is still connected

            :return Response:
            """
            conn_id = request.cookies.get('id')
            self.conn_manager.reset_connection_timer(conn_id)

            return Response(status=200)

    def is_job_done(self):
        """
        Convenience Function that calls StatusManager function of same name

        :return Boolean:
        """
        return self.status_manager.is_job_done()

    def get_status(self):
        """
        Convenience Function that calls StatusManager function of same name

        :return String:
        """
        return self.status_manager.get_status()

    def print_status(self):
        """
        Convenience Function that calls StatusManager function of same name

        :return:
        """
        self.status_manager.print_status()
        # TODO: Below Is a BAD Hot Fix, find real issue later
        # Issue is the connection cleanup timer stops running for some reason.
        self.conn_manager.cleanup_connections()

    def get_completed_tasks(self):
        """
        Returns completed tasks from the TaskManager

        :return List[Task]:
        """
        return self.task_manager.flush_finished_tasks()


# OVERLOADED DO NOT RENAME
def create_app(hyper_master: HyperMaster):
    """
    Creates and launches the master node application

    :param hyper_master:
    :return Flask app:
    """

    # create and configure the Flask app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')

    # load configurations if any exist (for Flask config)
    if hyper_master.test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(hyper_master.test_config)

    # TODO: optional step
    # ensure the instance folder exists so configurations can be added
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    # create the endpoints for job handling
    hyper_master.create_routes(app)

    return app
