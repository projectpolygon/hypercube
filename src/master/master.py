"""
Implemented fuctionality to run a master node for a distributed workload
"""

# External imports
from io import BytesIO
from json import loads
from os import environ, makedirs
from zlib import compress, error as CompressException
from flask import Flask, Response, jsonify, request, send_file

# Internal imports
import common.api.endpoints as endpoints
from common.api.types import MasterInfo
from common.logging import Logger
from common.networking import get_ip_addr
from .connection import ConnectionManager

logger = Logger()

class HyperMaster():
    """
    When the master is started, this class should be what the user application
    can import to begin using the features of the system on the master itself
    """

    def __init__(self, HOST="0.0.0.0", PORT=5678):
        self.host = HOST
        self.port = PORT
        self.test_config = None
        self.task_queue = []
        self.conn_manager: ConnectionManager = ConnectionManager()

    def start_server(self):
        """
        Starts the server
        """
        app = create_app(self)
        app.run(host=self.host, port=self.port, debug=True)

    def create_routes(self, app, job_file_name):
        """
        Creates the required routes
        """

        @app.route(f'/{endpoints.JOB}')
        # pylint: disable=W0612
        def get_job():
            """
            Endpoint to handle job request from the slave
            """
            conn_id = request.cookies.get('id')

            logger.log_info(f'Job request from {conn_id},\nSaving connection...')
            self.conn_manager.add_connection(conn_id)

            with open(job_file_name, "r") as job_file:
                # read and parse the JSON
                job_json = loads(job_file.read())
                return jsonify(job_json)

        @app.route(f'/{endpoints.FILE}/<int:job_id>/<string:file_name>', methods=["GET"])
        # pylint: disable=W0612
        def get_file(job_id: int, file_name: str):
            """
            Endpoint to handle file request from the slave
            """
            try:
                with open(file_name, "rb") as file:
                    logger.log_info(f'Sending {file_name} as part of job {job_id}')
                    file_data = file.read()
                    compressed_data = compress(file_data)
                    return send_file(
                        BytesIO(compressed_data),
                        mimetype='application/octet-stream',
                        as_attachment=True,
                        attachment_filename=file_name
                    )

            except CompressException as error:
                logger.log_error(error)
                return Response(status=500)

            except FileNotFoundError as error:
                logger.log_error(error)
                return Response(status=404)

            except Exception as error:
                logger.log_error(error)
                return Response(status=500)

        @app.route(f'/{endpoints.TASK}/<int:job_id>', methods=["GET"])
        # pylint: disable=W0612
        def get_task():
            """
            arguments: job_id: int
            read the message for information
            fetch task from the queue
            return this task "formatted" back to slave
            """

        @app.route(f'/{endpoints.TASK_DATA}/<int:job_id>/<int:task_id>', methods=["POST"])
        # pylint: disable=W0612
        def task_data():
            """
            arguments: job_id: int, task_id: int
            read rest of data as JSON and pass payload to application
            return 200 ok
            """

        @app.route(f'/{endpoints.DISCOVERY}')
        # pylint: disable=W0612
        def discovery():
            """
            Endpoint used for initial master discovery for the slave.
            Returns master information in json format to slave
            """
            master_info: MasterInfo = {
                "ip": get_ip_addr()
            }
            return jsonify(master_info)

        @app.route(f'/{endpoints.HEARTBEAT}')
        # pylint: disable=W0612
        def heartbeat():
            """
            Heartbeat recieved from a slave, indicating it is still connected
            """
            conn_id = request.cookies.get('id')
            logger.log_info(f'Updating connection [{conn_id}]...')
            self.conn_manager.reset_connection_timer(conn_id)

            return Response(status=200)

    # functions that can be overridden to do user programmable tasks
    # TODO: what do these take as arguments, and what do they return?

    def set_job_get_handle(self):
        """
        Bind a handle to each call to JOB_GET
        """

    def job_get_handle_func(self, arg):
        """
        do stuff
        """

    def set_task_get_handle(self):
        """
        Bind a handle to each call to TASK_GET
        """

    def task_get_handle_func(self, arg):
        """
        do stuff
        """

    def set_file_get_handle(self):
        """
        Bind a handle to each call to FILE_GET
        """

    def file_get_handle_func(self, arg):
        """
        do stuff
        """


# OVERLOADED DO NOT RENAME
def create_app(hyper_master: HyperMaster):
    """
    Creates and lauches the master node application
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

    job_file_name = ""
    if "HYPER_JOBFILE_NAME" in environ:
        logger.log_info('Using environment varible to set jobfile')
        job_file_name = environ.get("HYPER_JOBFILE_NAME")
    else:
        logger.log_info('Using provided jobfile')
        job_file_name = "jobfile"

    # TODO: optional step
    # ensure the instance folder exists so configurations can be added
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    # create the endpoints for job handling
    hyper_master.create_routes(app, job_file_name)

    return app


# TODO: normally, this would be imported
# as a module, and used in application code
if __name__ == "__main__":
    # create the hypermaster
    server = HyperMaster()

    # TODO: here would be where you would bind handler functions etc.

    # pass control to the server
    server.start_server()
