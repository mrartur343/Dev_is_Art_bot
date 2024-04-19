import csv

def get_all_items():
	rows = []
	all_items_dict = []
	with open("members_data/store_items.csv") as file:
		csv_reader = csv.reader(file, delimeter="|")
		fields = next(csv_reader)
		for row in csv_reader:
			rows.append(row)

	for i,col in enumerate(rows):
		collection_item = {}
		if len(col)>0:
			for j, item in enumerate(col):
				if type(item) == str:
					if "&" in item:
						item.replace('&', "\n")
				collection_item[fields[j]]=item
			all_items_dict.append(collection_item)

	return all_items_dict

def get_item_from_id(id):
	rows = []
	only_id = []
	with open("members_data/store_items.csv") as file:
		csv_reader = csv.reader(file, delimeter="|")
		fields = next(csv_reader)
		for row in csv_reader:
			only_id.append(row[0])
			rows.append(row)

	index = only_id.index(id)
	row = rows[index]
	collection_item = {}
	if len(row) > 0:
		for j, item in enumerate(row):
			if type(item) == str:
				if "&" in item:
					item.replace('&', "\n")
			collection_item[fields[j]] = item
		return collection_item

def append_item(name: str, description: str, price: int, author_id: int, stars: int, give_role_id: int):

	id = 0

	only_id = []
	with open("members_data/store_items.csv") as file:
		csv_reader = csv.reader(file, delimeter="|")
		fields = next(csv_reader)
		for row in csv_reader:
			only_id.append(row[0])

	while id in only_id:
		id+=1

	row = [id,name.replace('|', ' ').replace('\n', '&')
		, description.replace('|', ' ').replace('\n', '&')
		, price
		, author_id
		, stars
		, give_role_id]

	with open(f"members_data/store_items.csv", 'a', encoding='utf-8') as file:
		file.write('\n')
		csv_writer = csv.writer(file, delimiter='|')
		csv_writer.writerow(row)