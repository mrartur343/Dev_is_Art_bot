import asyncio
import json
import os.path
import shutil
import typing
from os import listdir
import os
from os.path import join, isfile

from subprocess import Popen
from savify import Savify
from savify.types import Type, Format, Quality
import spotipy
from savify.utils import PathHolder
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from tinytag import TinyTag
auth_manager = SpotifyClientCredentials(client_id="1a5350b67e5c4715b4ac9ac99e1b4b28",client_secret="2b0a1dc0bb094cabbc4e01cef163e125")
sp = spotipy.Spotify(auth_manager=auth_manager)

sfy = Savify(api_credentials=("1a5350b67e5c4715b4ac9ac99e1b4b28","2b0a1dc0bb094cabbc4e01cef163e125"), path_holder=PathHolder(downloads_path='downloaded_songs'), download_format=Format.MP3)
def get_server_radio(server_id:int) -> typing.List[typing.Dict[str, str]] | None:
	if os.path.exists(f"server_radios/{server_id}.json"):
		with open(f"server_radios/{server_id}.json", 'r') as file:
			return json.loads(file.read())

def get_all_songs_paths() -> typing.Tuple[typing.List[str],typing.List[str]]:
	all_songs_files = ["downloaded_songs/"+f for f in listdir(f"downloaded_songs") if
	                   isfile(join(f"downloaded_songs", f))]

	print("load title {}")
	all_songs_names=[]
	for f in listdir(f"downloaded_songs"):
		if isfile(join(f"downloaded_songs", f)):
			all_songs_names.append(TinyTag.get("downloaded_songs/"+f).title)


	return all_songs_names,all_songs_files


async def get_songs(url:str) -> typing.Tuple[typing.List[str], typing.List[str], typing.List[str]]:
	MAX_RETRIES=15
	retry_count=0

	uri = url.split("/")[-1].split("?")[0]

	while retry_count < MAX_RETRIES:
		try:
			results = sp.playlist_tracks(uri)

			songs_original = results['items']
			while results['next']:
				results = sp.next(results)
				songs_original.extend(results['items'])

			songs_names = [t["track"]["name"] for t in songs_original]

			songs_urls = ["https://open.spotify.com/track/" + t["track"]["uri"].split(":")[-1] for t in songs_original]

			songs_images = [t["track"]["album"]["images"][0]['url'] for t in songs_original]

			return songs_names, songs_urls,songs_images
		except Exception as e:
			print(f"Error encountered: {e}")
			print(f"Retrying... (Attempt {retry_count + 1} of {MAX_RETRIES})")
			retry_count+=1
			await asyncio.sleep(0.5)
	else:
		print(f"Failed to add chunk to playlist after {MAX_RETRIES} attempts. Skipping...")
		results = sp.playlist_tracks(uri)

async def get_songs_full_info(url:str) -> list:
	MAX_RETRIES=15
	retry_count=0

	uri = url.split("/")[-1].split("?")[0]

	while retry_count < MAX_RETRIES:
		try:
			results = sp.playlist_tracks(uri)

			songs_original = results['items']
			while results['next']:
				results = sp.next(results)
				songs_original.extend(results['items'])

			songs = [t['track'] for t in songs_original]

			return songs
		except Exception as e:
			print(f"Error encountered: {e}")
			print(f"Retrying... (Attempt {retry_count + 1} of {MAX_RETRIES})")
			retry_count+=1
			await asyncio.sleep(0.5)
	else:
		print(f"Failed to add chunk to playlist after {MAX_RETRIES} attempts. Skipping...")
		results = sp.playlist_tracks(uri)
async def playlist_name(url:str) -> typing.Tuple[typing.List[str], typing.List[str]]:
	MAX_RETRIES=15
	retry_count=0

	uri = url.split("/")[-1].split("?")[0]

	while retry_count < MAX_RETRIES:
		try:
			results = sp.user_playlist(user=None, playlist_id=uri, fields="name")


			return results['name']
		except Exception as e:
			print(f"Error encountered: {e}")
			print(f"Retrying... (Attempt {retry_count + 1} of {MAX_RETRIES})")
			retry_count+=1
			await asyncio.sleep(0.5)
	else:
		print(f"Failed to add chunk to playlist after {MAX_RETRIES} attempts. Skipping...")

		results = sp.user_playlist(user=None, playlist_id=uri, fields="name")

		return results['name']


async def song_download(song_url: str):
	p = Popen(['spotdl', song_url], cwd='downloaded_songs')
async def playlist_image(url: str):
	MAX_RETRIES=15
	retry_count=0
	while retry_count<MAX_RETRIES:
		try:
			returned= sp.playlist_cover_image(url.split("/")[-1].split("?")[0])[0]['url']
			return returned
		except Exception as e:
			print(f"Error encountered: {e}")
			print(f"Retrying... (Attempt {retry_count + 1} of {MAX_RETRIES})")
			retry_count+=1
			await asyncio.sleep(0.5)
	else:
		print(f"Failed to add chunk to playlist after {MAX_RETRIES} attempts. Skipping...")
		return