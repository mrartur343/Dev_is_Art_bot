import os
import sys

album_key = sys.argv[1]
filenames = os.listdir(".")
for file in filenames:
	if file.endswith('.mp3'):
		os.replace(file, f'songs/{album_key}/{file}')
		wait_check = False
		print(f"До альбому довантажено {file}")