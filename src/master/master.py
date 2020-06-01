import os
from flask import Flask, request, Response, jsonify, send_file
from io import BytesIO
import json
from zlib import compress, error as CompressException
from common.networking import get_ip_addr
import common.api.endpoints as endpoints


class HyperMaster():

    def __init__(self, HOST="0.0.0.0", PORT=5678):
        self.HOST = HOST
        self.PORT = PORT
        self.test_config = None
        self.task_queue = []
        self.connections = []

    def start_server(self):
        app = create_app(self)
        app.run(host=self.HOST, port=self.PORT, debug=True)

    def create_routes(self, app, job_file_name):

        # JOB_GET
        @app.route("/{}".format(endpoints.JOB), methods=["GET", "POST"])
        def get_job():
            with open(job_file_name, "r") as job_file:
                # read and parse the JSON
                job_json = json.loads(job_file.read())

                if request.is_json:
                    content = request.json()

                    # GLOBAL list for tracking slaves
                    # still need to work out how we want
                    # to use this
                    self.connections.append(content)
                return jsonify(job_json)

        @app.route("/{}/<int:job_id>/<string:file_name>".format(endpoints.FILE), methods=["GET"])
        def get_file(job_id: int, file_name: str):
            """
            Endpoint to handle file request from the slave
            """
            try:
                with open(file_name, "rb") as file:
                    print("INFO: sending {} as part of job {}".format(
                        file_name, job_id))
                    file_data = file.read()
                    compressed_data = compress(file_data)
                    return send_file(
                        BytesIO(compressed_data),
                        mimetype='application/octet-stream',
                        as_attachment=True,
                        attachment_filename=file_name
                    )

            except CompressException as e:
                print('Err:', e)
                return Response(status=500)

            except FileNotFoundError as e:
                print('Err:', e)
                return Response(status=404)

            except Exception as e:
                print('Err:', e)
                return Response(status=500)

        # TASK_GET
        @app.route("/{}/<int:job_id>".format(endpoints.TASK), methods=["GET"])
        def get_task(job_id: int):
            content = request.json
            # read the message for information
            # fetch task from the queue
            # return this task "formatted" back to slave

        # TASK_DATA
        @app.route("/{}/<int:job_id>/<int:task_id>".format(endpoints.TASK_DATA), methods=["POST"])
        def task_data(job_id: int, task_id: int):
            message_data = request.json
            # read rest of data as JSON and pass payload to application
            # return 200 ok

        @app.route("/{}".format(endpoints.DISCOVERY))
        def discovery():
            json_data = {"ip": get_ip_addr()}
            resp = Response(json_data, status=200)
            return resp

        @app.route("/{}".format(endpoints.HEARTBEAT))
        def heartbeat():
            return Response(status=200)

    # functions that can be overridden to do user programmable tasks
    # TODO: what do these take as arguments, and what do they return?
    def set_job_get_handle(self):
        """
        Bind a handle to each call to JOB_GET
        """
        pass

    def job_get_handle_func(self, arg):
        """
        do stuff
        """
        pass

    def set_task_get_handle(self):
        """
        Bind a handle to each call to TASK_GET
        """
        pass

    def task_get_handle_func(self, arg):
        """
        do stuff
        """
        pass

    def set_file_get_handle(self):
        """
        Bind a handle to each call to FILE_GET
        """
        pass

    def file_get_handle_func(self, arg):
        """
        do stuff
        """
        pass


# OVERLOADED DO NOT RENAME
def create_app(hyper_master: HyperMaster):

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
    if "HYPER_JOBFILE_NAME" in os.environ:
        print("INFO: using environment varible to set jobfile")
        job_file_name = os.environ.get("HYPER_JOBFILE_NAME")
    else:
        print("USING jobfile")
        job_file_name = "jobfile"

    # TODO: optional step
    # ensure the instance folder exists so configurations can be added
    try:
        os.makedirs(app.instance_path)
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
