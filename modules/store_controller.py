import json
import os.path
import typing
import discord
import jmespath

options_labels = [

	"Тінь",

	"Виноград"
	,

	"Паутина"
	,

	"Червоне полум'я"
	,

	"Чорне море"
	,

	"Діамант"
	,

	"Сніжок"
	,

	"Квітка"
	,

	"Хвоя"
	,

	"Великодка"
	,

	"Левада"
	,

	"Палючий пісок"
	,

	"Гарбуз"
	,

	"Вечірнє небо"
	,

	"Лимон"
	,

	"Світло"

]
def get_items()-> list:
	file_name = f"shop/items.csv"
	returned_collection = []
	rows = []
	fields = []

	with open('shop/items.json', 'r') as file:
		returned_collection = json.loads(file.read())
	return returned_collection
def get_user_items(user_id):
	with open("shop/user_items.json", 'r', encoding='utf-8') as file:
		users_items: dict = json.loads(file.read())

	if not str(user_id) in users_items:
		users_items[str(user_id)] = {}

	return users_items[str(user_id)]
def add_item(name: str, user_id: int, amount: int = 1):
	r_name = name.replace('|', ' ').replace('\n', '&')

	with open("shop/user_items.json", 'r', encoding='utf-8') as file:
		users_items: dict = json.loads(file.read())

	if not str(user_id) in users_items:
		users_items[str(user_id)] = {}

	if not r_name in users_items[str(user_id)]:
		users_items[str(user_id)][r_name] = 0
	users_items[str(user_id)][r_name] += amount


	with open("shop/user_items.json", 'w', encoding='utf-8') as file:
		json.dump(users_items,file)

def get_top() -> typing.List[typing.List[int]]:
	rows = []
	only_names = []
	with open("shop/user_cash.json",'r' ) as file:
		users = json.loads(file.read())
		for user in users:
			row = [user["user_id"], user['cash']]

			formated_row= []
			for el in row:
				formated_row.append(int(el))

			if len(row)>0:
				only_names.append(int(row[0]))
				rows.append(formated_row)
	rows.sort(key = lambda e: e[1],reverse=True)
	return rows

def get_user_cash(user_id: int):
	with open("shop/user_cash.json", 'r') as file:
		for user in json.loads(file.read()):
			if user['user_id']==user_id:
				return user

def get_all_id():
	with open("shop/user_cash.json", 'r') as file:
		return jmespath.search("[*][user_id]", json.loads(file.read()))


def change_cash(user_id: int, amount: int):
	result = []
	with open("shop/user_cash.json", 'r') as file:
		for user in json.loads(file.read()):
			if user['user_id']==user_id:
				user['cash']+=amount
		result.append(user)
	with open("shop/user_cash.json", 'w') as file:
		json.dump(result,file)

def item_create(name: str, price: int, description: str, author_id: int):
	with open("shop/items.json", 'r') as file:
		result = json.loads(file.read())
		result.append({"name": name, "price": price, "description": description, "author_id": author_id})
	with open("shop/items.json", 'w') as file:
		json.dump(result,file)


def get_item(name:str):
	with open("shop/items.json", 'r') as file:
		for item in json.loads(file.read()):
			if item['name']==name:
				return item


def buy_item(name:str, user_id: int):
	item = get_item(name)
	if item!=None:
		user = get_user_cash(user_id)

		if user['cash']>=item['price']:
			add_item(name, user_id, 1)
			change_cash(user_id,int( item['price'])*-1)
			change_cash(int(item['author_id']),int(item['price']))
			print('AAAAAAAAAA')

			return True

		return "cash"
	return "item"



