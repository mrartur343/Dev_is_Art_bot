import cv2
import numpy as np
import json
from skimage import io


def get_avarage_color(key_str: str):
	with open("other/average_color_cache.json", 'r') as file:
		cache = json.loads(file.read())
		if key_str in cache.keys():
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
