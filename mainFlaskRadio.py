import datetime
import io
import json
import wave
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



@app.route("/radio.mp3", methods=["GET"])
def streamwav():
	ip =flask.request.remote_addr
	channels_names = ["Alpha", "Beta", 'Gamma', "Delta"]
	channel = channels_names[int(flask.request.args.get('c'))]
	def generate():
		with open("other/current_play.json", 'r') as file:
			cp = json.loads(file.read())
			current_play_path = cp[channel][0]
			current_play_time = cp[channel][1]
			start_time = (datetime.datetime.now()-datetime.datetime.fromtimestamp(current_play_time)).seconds

		with (open(current_play_path, 'rb') as fmp3):

			# extract data


			asmp3 = AudioSegment.from_mp3(fmp3)[(start_time*1000):]

			buf = io.BytesIO()
			asmp3.export(buf, format='mp3')

			data_sent = CHUNK
			with buf as file2:
				while data_sent<os.path.getsize(current_play_path):
					data_sent+=CHUNK
					yield file2.read(CHUNK)
	return Response(generate(), mimetype="audio/mp3")


@app.route("/r/beta.mp3")
def r_beta():
	r = requests.get("http://devisart.xyz:11624/radio.mp3?c=1", stream=True)
	return Response(r.iter_content(chunk_size=1), mimetype='audio/mp3')

app.run(host='0.0.0.0', port=9010)