import json
import os.path
import typing
from os import listdir
from os.path import join, isfile

import requests
from bs4 import BeautifulSoup
import subprocess
import sys # for sys.executable (The file path of the currently using python)
from spotdl import __main__ as spotdl # To get the location of spotdl
from tinytag import TinyTag


def get_server_radio(server_id:int) -> typing.List[typing.Dict[str, str]] | None:
	if os.path.exists(f"server_radios/{server_id}.json"):
		with open(f"server_radios/{server_id}.json", 'r') as file:
			return json.loads(file.read())

def get_all_songs_paths() -> typing.List[typing.Tuple[str,str]]:
	all_songs_files = [f for f in listdir(f"server_radios") if
	                   isfile(join(f"server_radios", f))]

	all_songs_names = [TinyTag.get(f).title for f in listdir(f"server_radios") if
	                   isfile(join(f"server_radios", f))]


	return zip(all_songs_names,all_songs_files)


def get_songs(url:str) -> typing.List[typing.Tuple[str, str]]:

	r_onlineradio = requests.get(url).content

	soup = BeautifulSoup(r_onlineradio, 'html.parser')

	songs_names = [heading.text for heading in
	 soup.find_all('div', class_='encore-text encore-text-body-medium encore-internal-color-text-base btE2c3IKaOXZ4VNAb8WQ standalone-ellipsis-one-line')]

	songs_urls = [heading.text for heading in
	 soup.find_all('a', class_='btE2c3IKaOXZ4VNAb8WQ')]

	return zip(songs_names,songs_urls)

def song_download(track_url: str):
	subprocess.call('cd downloaded_songs', shell=True)
	subprocess.check_call([sys.executable, spotdl.__file__, track_url], shell=True)

def songs_download(radio_url: str):
	subprocess.call('cd downloaded_songs', shell=True)
	subprocess.check_call([sys.executable, spotdl.__file__, radio_url], shell=True)
