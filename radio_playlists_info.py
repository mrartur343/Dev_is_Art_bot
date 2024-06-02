import math
from os import listdir
from os.path import isfile, join
from typing import Dict, List

from tinytag import TinyTag
import json

with open('other/radio_playlists.json','r') as file:
	radio_playlists: Dict[str, List[str]] = json.loads(file.read())
with open('other/singles_names.json','r') as file:
	singles_names: List[str] = json.loads(file.read())
with open('other/albums_data.json','r') as file:
	albums_data: Dict[str, List[str]] = json.loads(file.read())
for radio_i, playlist in radio_playlists.items():
	print(f'----- {radio_i} -----')
	print(f'Total: {len(playlist)}')

	s = 0
	for p in playlist:
		if p in singles_names:
			s+=1

	print(f'Singles: {s}')
	print(f'Albums: {len(playlist)-s}')

	all_time=0
	for k in playlist:
		d = 0
		for file in [f for f in listdir(f"songs/{k}") if
				                          isfile(join(f"songs/{k}", f))]:
			audio_info = TinyTag.get(f"songs/{k}/{file}")
			if audio_info.duration != None:
				d += audio_info.duration
		all_time+=d
	print(f'Duration: {math.floor((all_time / 60) / 60)} h {math.floor((all_time % 3600) / 60)} m {math.floor(all_time % 60)} s')

	print()
	for k in playlist:
		print(f'{k}: {albums_data[k][0]}')
