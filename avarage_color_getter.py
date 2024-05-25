import cv
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

	pixels = np.float32(img.reshape(-1, 3))

	n_colors = 5
	criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 200, .1)
	flags = cv.KMEANS_RANDOM_CENTERS

	_, labels, palette = cv.kmeans(pixels, n_colors, None, criteria, 10, flags)
	_, counts = np.unique(labels, return_counts=True)

	dom = list(palette[np.argmax(counts)])
	result = []
	for d in dom:
		result.append(round(d))
	with open('other/average_color_cache.json', 'w') as file:
		cache[key_str]=result
		json.dump(cache,file)
	return result

#