import flask
import json
from flask import Flask

app = Flask(__name__)

@app.route("/")
def transmit():
	f = open('db.txt', 'r')
	output = f.read()
	return "{"+output[:-1]+"}"

@app.route("/receive", methods=['GET', 'POST'])
def receive():
	to_return = ""
	to_return = json.dumps(flask.request.args.items())
	f = open('db.txt','a')
	f.write(to_return+",")
	return to_return

if __name__ == "__main__":
	app.debug = True	
	app.run(host='0.0.0.0')
