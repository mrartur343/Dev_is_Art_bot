import json
import os.path
import typing
from os import listdir
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

def get_all_songs_paths() -> typing.List[typing.Tuple[str,str]]:
	all_songs_files = [f for f in listdir(f"server_radios") if
	                   isfile(join(f"server_radios", f))]

	all_songs_names = [TinyTag.get(f).title for f in listdir(f"server_radios") if
	                   isfile(join(f"server_radios", f))]


	return zip(all_songs_names,all_songs_files)


def get_songs(url:str) -> typing.List[typing.Tuple[str, str]]:

	uri = url.split("/")[-1].split("?")[0]

	print(sp.playlist_tracks(uri,limit=1000))

	songs_names = [t["track"]["name"] for t in sp.playlist_tracks(uri,limit=1000)['items']]

	songs_urls = ["https://open.spotify.com/track/"+t["track"]["uri"] for t in sp.playlist_tracks(uri,limit=1000)['items']]

	return zip(songs_names,songs_urls)

def song_download(track_url: str):
	subprocess.call('cd downloaded_songs', shell=True)
	subprocess.check_call([sys.executable, spotdl.__file__, track_url], shell=True)

def songs_download(radio_url: str):
	subprocess.call('cd downloaded_songs', shell=True)
	subprocess.check_call([sys.executable, spotdl.__file__, radio_url], shell=True)
