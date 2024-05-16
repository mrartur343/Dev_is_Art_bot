import cv2 as cv
import numpy as np
import json
from skimage import io


def get_avarage_color(key_str: str):
	with open("other/average_color_cache.json", 'r') as file:
		cache = json.loads(file.read())
		if key_str in cache.keys():
			return cache[key_str]

	img = cv.imread("a.png")
	img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

	dim = (500, 300)
	# resize image
	img = cv.resize(img, dim, interpolation=cv.INTER_AREA)

	result = []
	for i,d in enumerate(list(np.average(img, axis=(0, 1)))):
		result.append(round(d))
	with open('other/average_color_cache.json', 'w') as file:
		cache[key_str]=result
		json.dump(cache,file)
	return result\

#