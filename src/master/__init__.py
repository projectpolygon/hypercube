import os
from flask import Flask, request, Response, jsonify
import json
import base64
from common.networking import *
from common import *

# OVERLOADED DO NOT RENAME
def create_app(test_config=None):
	
	# create and configure the Flask app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(SECRET_KEY='dev')

	# load configurations if any exist (for Flask config)
	if test_config is None:
	# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)
	
	job_file_name = ""
	if "HYPER_JOBFILE_NAME" in os.environ:
		print("INFO: using environment varible to set jobfile")
		job_file_name = os.environ.get("HYPER_JOBFILE_NAME")
		print(job_file_name)
	else:
		print("USING jobfile")
		job_file_name = "jobfile"

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	set_routes(app, job_file_name)
	return app


def set_routes(app, job_file_name):
    # TODO: replace with something better, maybe persistence??
	jobs = []

	@app.route("/JOB_GET", methods=["GET", "POST"])
	def job_get():
		with open(job_file_name, "r") as job_file:
			# read and parse the JSON 
			job_json = json.loads(job_file.read())
			print(job_json)

			#job_response = Response(job_json, status=200)
		
			if request.is_json:
				content = request.json()
				# GLOBAL for tracking slaves
				jobs.append(content)

			# TODO: implement exception handling
			return jsonify(job_json)
	
	@app.route("/FILE_GET/<int:job_id>/<string:file_name>", methods=["GET"])
	def file_get(job_id:int, file_name:str):
		print(job_id)
		print(file_name)

		file_data = {"job_id":job_id, "file_name":file_name, "payload":None}

		with open(file_name, "rb") as file:
			file_data["payload"] = base64.b64encode(file.read()).decode("ascii")
			return jsonify(file_data)

	@app.route("/TASK_GET/<int:job_id>", methods=["GET"])
	def task_get(job_id: int):
		content = request.json
		# read the message for information
		# fetch task from the queue
		# return this task "formatted" back to slave

	@app.route("/TASK_DATA/<int:job_id>/<int:task_id>", methods=["POST"])
	def task_data(job_id:int, task_id:int):
		message_data = request.json
		
		# read rest of data as JSON and pass payload to application
		# return 200 ok
	
	@app.route("/HEARTBEAT")
	def heartbeat():
		json_message = {"ip": get_ip_addr(),"status":200}
		response_message = Response(json_message, status=200)
		return response_message
    #@app.route("/job")
    #def get_first_job():
    #    return get_job()

    #@app.route("/job/<int:job_id>")
    #def get_job(job_id: int):
    #    try:
    #        return jobs[job_id]
    #    except Exception as e:
    #        return {"job_id": -1}

    #@app.route("/job/<int:job_id>/task")
    #def get_task(job_id: int):
    #    job = get_job(job_id)
    #    for task in job["tasks"]:
     #       if task["status"] == "available":
    #            return task
#
     #   return {"task_id": -1}

 #   @app.route("/job/<int:job_id>/task/<int:task_id>/data", methods=["POST"])
 #   def set_task_data(job_id: int, task_id: int):
 #       task = request.json
 #       job = get_job(job_id)
 #       job["tasks"][task_id] = task
 #      # TODO: implement exception handling
 #       return {"successful": true}


    # @app.route("/job/file/<string:file_name>")
    # def get_file(file_name):
    #     file_path = os.path.join(os.getcwd(), __name__, file_name)
    #     file = open(file_path, "r")
    #     return file.read()
