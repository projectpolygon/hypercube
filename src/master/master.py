import os
from flask import Flask, request, Response, jsonify
import json
import base64
from common.networking import *
from common import *

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
def create_app(hyper_master : HyperMaster):
	
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
	create_routes(hyper_master, app, job_file_name)

	return app

# TODO these functions might be better suited as member functions
def create_routes(hyper_master, app, job_file_name):
    
	# JOB_GET
	@app.route("/JOB_GET", methods=["GET", "POST"])
	def job_get():
		with open(job_file_name, "r") as job_file:
			# read and parse the JSON 
			job_json = json.loads(job_file.read())
		
			if request.is_json:
				content = request.json()

				# GLOBAL list for tracking slaves
				# still need to work out how we want
				# to use this
				hyper_master.connections.append(content)
			return jsonify(job_json)
	
	# FILE_GET
	@app.route("/FILE_GET/<int:job_id>/<string:file_name>", methods=["GET"])
	def file_get(job_id:int, file_name:str):
		print("INFO: sending {} as part of job {}".format(file_name, job_id))
		
		# dictionary for response to the slave
		file_data = {"job_id":job_id, "file_name":file_name, "payload":None}

		# encode as base64, but decode as ASCII so it can be transferred over JSON
		try:
			with open(file_name, "rb") as file:
				file_data["payload"] = base64.b64encode(file.read()).decode("ascii")
				return jsonify(file_data)
		except Exception as e:
			print("ERR: file `{}` not found".format(file_name))
			return Response(status=404)

	# TASK_GET
	@app.route("/TASK_GET/<int:job_id>", methods=["GET"])
	def task_get(job_id: int):
		content = request.json
		# read the message for information
		# fetch task from the queue
		# return this task "formatted" back to slave

	# TASK_DATA
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

# TODO: normally, this would be imported 
# as a module, and used in application code
if __name__ == "__main__":
	# create the hypermaster 
	server = HyperMaster()

	# TODO: here would be where you would bind handler functions etc.

	# pass control to the server
	server.start_server()
