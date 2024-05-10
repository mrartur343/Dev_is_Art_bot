import os

def download_album(album_url:str,album_key:str):
	os.system(f'spotdl {album_url}')
	filenames = next(os.walk(""), (None, None, []))[2]
	for file in filenames:
		if file.endswith('.mp3'):
			os.replace(file, f'songs/{album_key}/{file}')
