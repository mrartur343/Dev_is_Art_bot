import os


def download_album(album_url:str,album_key:str,log_channel=None):
	os.system(f"""spotdl download {album_url} --port 2099 --threads 10 && python modules/mp3_mover.py {album_key}""")
	print(f'Пройшло більш ніж 60 секунд з останнього завантаженного треку, альбом готовий!')


