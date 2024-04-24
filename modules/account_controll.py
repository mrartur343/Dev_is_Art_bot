import json

import jmespath

from modules import store_controller


def all_achievements():
	with open("shop/achievements.json", 'r', encoding='utf-8') as file:
		loaded = json.loads(file.read())

		achievements = {}

		for k, v in loaded.items():
			achievements[k] = v
			for i, id_str in enumerate(v['members']):
				achievements[k][i] = int(id_str)

		return achievements


def member_achievements(member_id):
	with open("shop/achievements.json", 'r', encoding='utf-8') as file:
		loaded = json.loads(file.read())

		achievements = {}

		for k, v in loaded.items():
			achievements[k] = v
			print(achievements)
			for i, id_str in enumerate(v['members']):
				achievements[i] = int(id_str)
		member_achievements = {}

		for k, v in loaded.items():
			if member_id in v['members']:
				member_achievements[k] = v

		return member_achievements

def get_all_id():

	return_id= []
	with open("shop/achievements.json", 'r', encoding='utf-8') as file:
		loaded = json.loads(file.read())

	for achiev, info in loaded.items():
		for m_id in info['members']:
			if not (int(m_id) in return_id):
				return_id.append(int(m_id))

	store_id = store_controller.get_all_id()

	for m_id in store_id:
		if not (m_id in return_id):
			return_id.append(m_id)

	return return_id


def create(key_name: str, name: str, description: str):
	with open("shop/achievements.json", 'r', encoding='utf-8') as file:
		loaded = json.loads(file.read())

	loaded[key_name] = {"name": name, "description": description, "members": []}

	with open("shop/achievements.json", 'w', encoding='utf-8') as file:
		json.dump(loaded, file)


def add_to_member(achievement_key: str, member_id: int):
	with open("shop/achievements.json", 'r', encoding='utf-8') as file:
		loaded = json.loads(file.read())

	loaded[achievement_key]["members"].append(member_id)

	with open("shop/achievements.json", 'w', encoding='utf-8') as file:
		json.dump(loaded, file)

