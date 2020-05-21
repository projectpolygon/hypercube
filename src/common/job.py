import json
from common.message import *


class Job():
	def load_from_file(self, path):
		try:
			with open(path, 'r') as jobfile:
				self.parsed_file = json.loads(jobfile.read())
				return True
		except Exception as e:
			print(e)
			return False
	
	def load_from_bytes(self, data):
		self.parsed_file = json.loads(data)
		self.job_id = self.parsed_file.get("job_id")
	
	def get_message(self):
		message = Message(MessageType.JOB_DATA)
		message.meta_data.job_id = self.parsed_file.get("job_id")
		message.job_files = self.parsed_file.get("filenames")
		return message

if __name__ == "__main__":
	job = Job()
	job.load_from_file("api/new_job.json")
