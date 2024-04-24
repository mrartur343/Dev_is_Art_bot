import csv
import json
import os.path
import typing
import discord
options_labels = [

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

	with open(file_name, "r") as file:
		csv_reader = csv.reader(file, delimiter='|')
		fields = next(csv_reader)
		for item in csv_reader:
			rows.append(item)
	for i,col in enumerate(rows):
		collection_item = {}
		if len(col)>0:
			for j, item in enumerate(col):
				if fields[j]=='price':
					collection_item[fields[j]] = int(item)
				else:
					collection_item[fields[j]] = item
			returned_collection.append(collection_item)
	return returned_collection
def get_user_items(user_id):
	with open("shop/user_items.json", 'r', encoding='utf-8') as file:
		users_items: dict = json.loads(file.read())

	if not str(user_id) in users_items:
		users_items[str(user_id)] = {}

	return users_items[str(user_id)]
def add_item(name: str, user_id: int, amount: int):
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

def get_user_cash(user_id: int):
	rows = []
	only_names = []
	with open("shop/user_cash.csv",'r' ) as file:
		csv_reader = csv.reader(file, delimiter="|")
		fields = next(csv_reader)
		for row in csv_reader:
			if len(row)>0:
				only_names.append(int(row[0]))
				rows.append(row)
	if user_id in only_names:
		index = only_names.index(user_id)
	else:
		return {'user_id': user_id, 'cash': 0}
	row = rows[index]
	collection_item = {}
	if len(row) > 0:
		for j, item in enumerate(row):
			if type(item) == str:
				if "&" in item:
					item.replace('&', "\n")
			collection_item[fields[j]] = int(item)
		return collection_item

def get_all_id():
	rows = []
	only_names = []
	with open("shop/user_cash.csv",'r' ) as file:
		csv_reader = csv.reader(file, delimiter="|")
		fields = next(csv_reader)
		for row in csv_reader:
			if len(row)>0:
				only_names.append(int(row[0]))
				rows.append(row)

	return only_names


def change_cash(user_id: int, amount: int):
	create_check = True
	new_rows = []
	with open("shop/user_cash.csv", 'r', encoding='utf-8') as file:
		reader = csv.reader(file, delimiter='|')

		fields = next(reader)
		for row in reader:
			if len(row)>0:
				new_row = []
				for v in row:
					new_row.append(int(v))
				if int(new_row[0])==user_id:
					print(f"am: {new_row[1]}")
					new_row[1]+=amount
					print(f"am2: {new_row[1]}")
					create_check = False
				new_rows.append(new_row)
	if create_check:
		with open('shop/user_cash.csv', 'a') as file:
			file.write('\n')
			writer = csv.writer(file, delimiter='|')

			writer.writerow([user_id, 0])
		return change_cash(user_id, amount)

	with open('shop/user_cash.csv', 'w') as file:
		file.write("")
	with open('shop/user_cash.csv', 'a') as file:

		writer = csv.writer(file, delimiter='|')

		writer.writerow(fields)

		for row in new_rows:
			writer.writerow(row)



def item_create(name: str, price: int, description: str, author_id: int):
	file_name = "shop/items.csv"
	row = [
		name.replace('|', ' ').replace('\n', '&'),
		price,
		description.replace('|', ' ').replace('\n', '&'),
		author_id
	]
	with open(file_name, 'a') as file:
		writer = csv.writer(file, delimiter='|')
		file.write('\n')
		writer.writerow(row)


def get_item(name:str):
	rows = []
	only_names = []
	with open("shop/items.csv") as file:
		csv_reader = csv.reader(file, delimiter="|")
		fields = next(csv_reader)
		for row in csv_reader:
			if len(row)>0:
				only_names.append(row[0])
				rows.append(row)
	if name.replace('|', ' ').replace('\n', '&') in only_names:
		index = only_names.index(name.replace('|', ' ').replace('\n', '&'))
	else:
		return None
	row = rows[index]
	collection_item: typing.Dict[str, str|int|str] = {}
	if len(row) > 0:
		for j, item in enumerate(row):
			if type(item) == str:
				if "&" in item:
					item.replace('&', "\n")
			if fields[j]=='price':
				collection_item[fields[j]] = int(item)
			else:
				collection_item[fields[j]] = item
		return collection_item


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



