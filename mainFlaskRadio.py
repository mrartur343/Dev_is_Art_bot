import datetime
import json
import wave
import os.path

import flask
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



@app.route("/radio", methods=["GET"])
def streamwav():
	ip =flask.request.remote_addr
	channels_names = ["Alpha", "Beta", 'Delta', "Gamma"]
	channel = channels_names[int(flask.request.args.get('c'))]
	def generate():
		with open("other/current_play.json", 'r') as file:
			cp = json.loads(file.read())
			current_play_path = cp[channel][0]
			current_play_time = cp[channel][1]
		if not os.path.exists(f"tmp/{current_play_path.split('/')[2]}.wav"):
			new_play = AudioSegment.from_mp3(current_play_path)
			new_play.export(f"tmp/{current_play_path.split('/')[2]}.wav", format="wav")
		with wave.open(f"tmp/{current_play_path.split('/')[2]}.wav", "rb") as fwav:
			start = (datetime.datetime.now() - datetime.datetime.fromtimestamp(current_play_time)).seconds
			nchannels = fwav.getnchannels()
			sampwidth = fwav.getsampwidth()
			framerate = fwav.getframerate()
			# set position in wave to start of segment
			fwav.setpos(int(start * framerate))
			# extract data

			data = fwav.readframes(fwav.getnframes()*framerate)

			with wave.open(f"tmp/{ip}.wav", 'wb') as outfile:
				outfile.setnchannels(nchannels)
				outfile.setsampwidth(sampwidth)
				outfile.setframerate(framerate)
				outfile.setnframes(int(len(data) / sampwidth))
				outfile.writeframes(data)
			with open(f'tmp/{ip}.wav', 'rb') as file2:
				yield file2.read()
	return Response(generate(), mimetype="audio/wav")

app.run(host='0.0.0.0', port=9010)