import datetime
import io
import json
import wave
import os.path
from subprocess import Popen, PIPE
import os.path

import flask
import requests
from pydub import AudioSegment
import os, shutil
from flask import Flask, Response, render_template
import discord

folder = 'tmp'
for filename in os.listdir(folder):
	file_path = os.path.join(folder, filename)
	try:
		if os.path.isfile(file_path) or os.path.islink(file_path):
			os.unlink(file_path)
		elif os.path.isdir(file_path):
			shutil.rmtree(file_path)
	except Exception as e:
		print('Failed to delete %s. Reason: %s' % (file_path, e))

app = Flask(__name__, template_folder='')
app.config['UPLOAD_FOLDER'] = '/'



CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5

PREFIX = "songs/"
FORMAT = ("mp3", "audio/mpeg")
def ffmpeg_generator(fn,start_time):
	process = Popen(["ffmpeg", "-hide_banner", "-loglevel", "panic", "-ss", str(start_time), "-i", fn, "-f", FORMAT[0], "-"], stdout=PIPE)
	while True:
		print("ffmpeg gen")
		data = process.stdout.read(1024)
		yield data

@app.route("/radio", methods=["GET"])
def streamwav():
	print("streamwav")
	channels_names = ["Alpha", "Beta", 'Gamma', "Delta"]
	channel = channels_names[int(flask.request.args.get('c'))]
	with open("other/current_play.json", 'r') as file:
		cp = json.loads(file.read())
		current_play_path = cp[channel][0]
		current_play_time = cp[channel][1]

	path = os.path.normpath("/" + current_play_path).lstrip("/")

	start_time = (datetime.datetime.now()-datetime.datetime.fromtimestamp(current_play_time)).seconds
	return Response(ffmpeg_generator(os.path.join(PREFIX, path),start_time), mimetype=FORMAT[1])



@app.route('/r/beta')
def radio_beta():
	"""Video streaming home page."""
	return flask.stream_template('index.html', radio_index =1 , radio_name = 'Beta')


app.run(host='0.0.0.0', port=9010)