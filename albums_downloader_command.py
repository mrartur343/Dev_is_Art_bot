import sys
from bs4 import BeautifulSoup
import os, json
from modules import album_downloader
import requests


def get_album_name_and_key(url: str):
	r_onlineradio = requests.get(url).content

	soup = BeautifulSoup(r_onlineradio, 'html.parser')

	album_name = [heading.text for heading in
						 soup.find_all('h1', class_='Type__TypeElement-sc-goli3j-0 ofaEA gj6rSoF7K4FohS2DJDEm')][0]
	album_key = url[-22:]
	return (album_name,album_key)

album_url = sys.argv[1]
single_check = bool(int(sys.argv[2]))

print(album_url)

print(single_check)

album_name, album_key = get_album_name_and_key(url=album_url)
print('wait...')
os.mkdir(f"songs/{album_key}")
with open("other/albums_data.json", 'r') as file:
	albums_data = json.loads(file.read())
albums_data[album_key]=[album_name,album_url]
with open("other/albums_data.json", 'w') as file:
	json.dump(albums_data,file)

with open("other/album_likes.json", 'r') as file:
	album_likes = json.loads(file.read())
album_likes[album_key]=[]
with open("other/album_likes.json", 'w') as file:
	json.dump(album_likes,file)

if single_check:
	with open("other/singles_names.json", 'r') as file:
		singles = json.loads(file.read())
	singles.append(album_key)
	with open("other/singles_names.json", 'w') as file:
		json.dump(singles,file)

print(f"Успішно створено [**{album_name}**]({album_url}) ({album_key})")


album_downloader.download_album(album_url,album_key)