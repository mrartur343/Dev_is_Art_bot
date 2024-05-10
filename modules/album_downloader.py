import os

async def download_album(album_url:str,album_key:str):
	os.system(f'spotdl {album_url}')
	mp3_check = True
	while mp3_check:
		for file in os.listdir('modules'):
			if file.endswith('.mp3'):
				os.replace(f'modules/{file}', f'songs/{album_key}/{file}')
				mp3_check=False
