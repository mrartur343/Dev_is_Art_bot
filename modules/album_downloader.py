import os


def download_album(album_url:str,album_key:str,log_channel=None):

	os.system(f"""cd songs/{album_key};spotdl download {album_url} --port 2099 --threads 20""")
	print(f'Альбом готовий!')


