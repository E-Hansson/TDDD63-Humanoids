import flask
import json
from flask import Flask

app = Flask(__name__)
db = lambda x: open('db.txt', x)

@app.route("/")
def transmit():
	f = db('r')
	output = f.read()
	return "["+output[:-1]+"]"

@app.route("/receive", methods=['GET', 'POST'])
def receive():
	to_return = ""
	to_return = json.dumps(flask.request.args.items())
	f = db('a')
	f.write(to_return+",")
	return to_return

@app.route("/newgame")
def newgame():
	f = db('w')
	f.write("")
	return "New game, resetting db"

if __name__ == "__main__":
	app.debug = True	
	app.run(host='0.0.0.0')
