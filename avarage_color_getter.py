import cv2
import numpy as np
import json
from skimage import io


def get_avarage_color(key_str: str):
	cache={}
	with open("other/average_color_cache.json", 'r') as file:
		if key_str in json.loads(file.read()).keys():
			cache=json.loads(file.read())
			return cache[key_str]
	img = io.imread("a.png")[:, :, :-1]

	dominant = img.mean(axis=0).mean(axis=0)
	result = []
	for i,d in enumerate(list(dominant)):
		result.append(round(d))
	with open('other/average_color_cache.json', 'w') as file:
		cache[key_str]=result
		json.dump(cache,file)
	return result