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

	pixels = np.float32(img.reshape(-1, 3))

	n_colors = 5
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
	flags = cv2.KMEANS_RANDOM_CENTERS

	_, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
	_, counts = np.unique(labels, return_counts=True)

	dominant = palette[np.argmax(counts)]
	result = []
	for i,d in enumerate(list(dominant)):
		result.append(round(d))
	with open('other/average_color_cache.json', 'w') as file:
		cache[key_str]=result
		json.dump(cache,file)
	return result