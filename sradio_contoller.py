import json
import os.path
import typing
from os import listdir
import os
from os.path import join, isfile
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import subprocess
import sys # for sys.executable (The file path of the currently using python)
from spotdl import __main__ as spotdl # To get the location of spotdl
from tinytag import TinyTag

auth_manager = SpotifyClientCredentials(client_id="1a5350b67e5c4715b4ac9ac99e1b4b28",client_secret="2b0a1dc0bb094cabbc4e01cef163e125")
sp = spotipy.Spotify(auth_manager=auth_manager)
def get_server_radio(server_id:int) -> typing.List[typing.Dict[str, str]] | None:
	if os.path.exists(f"server_radios/{server_id}.json"):
		with open(f"server_radios/{server_id}.json", 'r') as file:
			return json.loads(file.read())

def get_all_songs_paths() -> typing.Tuple[typing.List[str],typing.List[str]]:
	all_songs_files = ["downloaded_songs/"+f for f in listdir(f"downloaded_songs") if
	                   isfile(join(f"downloaded_songs", f))]

	all_songs_names = [TinyTag.get("downloaded_songs/"+f).title for f in listdir(f"downloaded_songs") if
	                   isfile(join(f"downloaded_songs", f))]


	return all_songs_names,all_songs_files


def get_songs(url:str) -> typing.Tuple[typing.List[str], typing.List[str]]:

	uri = url.split("/")[-1].split("?")[0]


	results = sp.playlist_tracks(uri)
	songs_original = results['items']
	while results['next']:
		results = sp.next(results)
		songs_original.extend(results['items'])

	songs_names = [t["track"]["name"] for t in songs_original]

	songs_urls = ["https://open.spotify.com/track/"+t["track"]["uri"] for t in songs_original]

	return songs_names, songs_urls

def songs_download(radio_url: str):
	os.system(f"ls;cd downloaded_songs;spotdl download {radio_url} --port 2099 --threads 20")

def songs_downloads(radio_url: str):
	os.system(f"ls;cd downloaded_songs;spotdl download {radio_url} --port 2099 --threads 20")
