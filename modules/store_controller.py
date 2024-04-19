import csv
import json
import typing

def get_items()-> list:
	file_name = f"shop/items.csv"
	returned_collection = []
	rows = []
	fields = []

	with open(file_name, "r", encoding='utf-8') as file:
		csv_reader = csv.reader(file, delimiter='|')
		fields = next(csv_reader)
		for item in csv_reader:
			rows.append(item)
	for i,col in enumerate(rows):
		collection_item = {}
		if len(col)>0:
			for j, item in enumerate(col):
				collection_item[fields[j]]=item
			returned_collection.append(collection_item)
	return returned_collection
def add_item(name: str, user_id: int, amount: int):
	r_name = name.replace('|', ' ').replace('\n', '&')

	with open("shop/user_items.json", 'r', encoding='utf-8') as file:
		users_items: dict = json.loads(file.read())

	if not user_id in users_items:
		users_items[user_id] = {}

	if not r_name in users_items[user_id]:
		users_items[user_id][r_name] = 0
	users_items[user_id][r_name] += amount

def get_user_cash(user_id: int):
	rows = []
	only_names = []
	with open("shop/user_cash.csv",'r', encoding='utf-8', ) as file:
		csv_reader = csv.reader(file, delimeter="|")
		fields = next(csv_reader)
		for row in csv_reader:
			only_names.append(row[0])
			rows.append(row)
	if user_id in only_names:
		index = only_names.index(user_id)
	else:
		return None
	row = rows[index]
	collection_item = {}
	if len(row) > 0:
		for j, item in enumerate(row):
			if type(item) == str:
				if "&" in item:
					item.replace('&', "\n")
			collection_item[fields[j]] = item
		return collection_item


def change_cash(user_id: int, amount: int):
	create_check = False
	new_rows = []
	with open("shop/user_cash.csv", 'r', encoding='utf-8') as file:
		reader = csv.reader(file, delimiter='|')

		fields = next(reader)
		for row in reader:
			new_row = row
			if new_row[0]==user_id:
				new_row[1]+=amount
				break
			new_rows.append(new_row)
		else:
			create_check = True

	if create_check:
		with open('shop/user_cash.csv', 'a') as file:

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
			collection_item[fields[j]] = item
		return collection_item


def buy_item(name:str, user_id: int):
	item = get_item(name)
	if item!=None:
		user = get_user_cash(user_id)
		if user['cash']>=item['price']:
			add_item(name, user_id, 1)
			change_cash(user_id, item['price']*-1)
			change_cash(user_id, item['author_id'])

			return True

		return "cash"
	return "item"

