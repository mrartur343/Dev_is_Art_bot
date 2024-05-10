import os
import time

import discord


async def download_album(album_url:str,album_key:str,log_channel: discord.TextChannel):
	os.system(f'spotdl {album_url}')
	wait_check = True
	timer = time.time()
	while wait_check or timer-time.time()>-60:
		filenames = os.listdir(".")
		for file in filenames:
			if file.endswith('.mp3'):
				os.replace(file, f'songs/{album_key}/{file}')
				timer = time.time()
				wait_check=False
				await log_channel.send(f"До альбому довантажено {file}")
				print(f"До альбому довантажено {file}")
	await log_channel.send(f'Пройшло більш ніж 60 секунд з останнього завантаженного треку, альбом готовий!')
	print(f'Пройшло більш ніж 60 секунд з останнього завантаженного треку, альбом готовий!')


