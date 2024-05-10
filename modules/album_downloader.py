import os

def download_album(album_url:str,album_key:str):
	os.system(f'spotdl {album_url}')
	wait_check = True
	while wait_check:
		filenames = os.listdir(".")
		for file in filenames:
			print(file)
			if file.endswith('.mp3'):
				os.replace(file, f'songs/{album_key}/{file}')
				wait_check=False
