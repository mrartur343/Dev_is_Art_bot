import asyncio
import os
import time

import discord


def download_album(album_url:str,album_key:str,log_channel=None):
	os.system(f'spotdl --port 1488 {album_url}')
	wait_check = True
	timer = time.time()
	while wait_check or timer-time.time()>-60:
		asyncio.sleep(5)
		filenames = os.listdir(".")
		for file in filenames:
			if file.endswith('.mp3'):
				os.replace(file, f'songs/{album_key}/{file}')
				timer = time.time()
				wait_check=False
				print(f"До альбому довантажено {file}")
	print(f'Пройшло більш ніж 60 секунд з останнього завантаженного треку, альбом готовий!')


