import os
import sys
import json

album_key = sys.argv[1]

with open('other/album_likes.json', 'r') as file:
	result: dict = json.loads(file.read())

	if album_key in result:
		del(result[album_key])

with open('other/album_likes.json', 'w') as file:
	json.dump(result,file)


with open('other/albums_data.json', 'r') as file:
	result: dict = json.loads(file.read())

	if album_key in result:
		del(result[album_key])

with open('other/albums_data.json', 'w') as file:
	json.dump(result,file)

with open('other/albums_images_cache.json', 'r') as file:
	result: dict = json.loads(file.read())

	if album_key in result:
		del(result[album_key])

with open('other/albums_images_cache.json', 'w') as file:
	json.dump(result,file)

with open('other/songs_lists_cache.json', 'r') as file:
	result: dict = json.loads(file.read())

	if album_key in result:
		del(result[album_key])

with open('other/songs_lists_cache.json', 'w') as file:
	json.dump(result,file)



with open('other/singles_names.json', 'r') as file:
	result: list = json.loads(file.read())

	if album_key in result:
		result.remove(album_key)

with open('other/songs_lists_cache.json', 'w') as file:
	json.dump(result,file)


os.rmdir(f'songs/{album_key}')