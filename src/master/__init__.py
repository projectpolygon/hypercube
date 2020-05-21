import os
from flask import Flask, request

from common.networking import *
from common import *


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    set_routes(app)

    return app


def set_routes(app):
    # TODO: replace with something better, maybe persistence??
    jobs = []

    @app.route("/job/create", methods=["POST"])
    def create_job():
        content = request.json
        jobs.append(content)
        # TODO: implement exception handling
        return {"successful": True}

    @app.route("/beacon")
    def beacon():
        return {"ip": get_ip_addr()}

    @app.route("/job")
    def get_first_job():
        return get_job()

    @app.route("/job/<int:job_id>")
    def get_job(job_id: int = 0):
        try:
            return jobs[job_id]
        except Exception as e:
            return {"job_id": -1}

    @app.route("/job/<int:job_id>/task")
    def get_task(job_id: int):
        job = get_job(job_id)
        for task in job["tasks"]:
            if task["status"] == "available":
                return task

        return {"task_id": -1}

    @app.route("/job/<int:job_id>/task/<int:task_id>/data", methods=["POST"])
    def set_task_data(job_id: int, task_id: int):
        task = request.json
        job = get_job(job_id)
        job["tasks"][task_id] = task
        # TODO: implement exception handling
        return {"successful": true}


    # @app.route("/job/file/<string:file_name>")
    # def get_file(file_name):
    #     file_path = os.path.join(os.getcwd(), __name__, file_name)
    #     file = open(file_path, "r")
    #     return file.read()
