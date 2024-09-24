import json
import datetime
import os.path

def get_collection(name: str)-> list:

	with open(f"art_collections/{name}.json", 'r') as file:
		return json.loads(file.read())
def collection_append(collection_name: str, name: str, description: str, author: str, url: str):
	with open(f"art_collections/{collection_name}.json", 'r') as file:
		collection = json.loads(file.read())
		collection.append({'name': name, "description": description,"author": author, "url": url})
	with open(f"art_collections/{collection_name}.json", 'w') as file:
		json.dump(collection,file)

