import csv
import datetime
import os.path
def posts_edit(a_id):

	if not os.path.exists(f"posts/{a_id}.csv"):
		return
	file_name = f"posts/{a_id}.csv"
	returned_collection = []
	rows = []
	fields = []


	with open(file_name, "r", encoding='utf-8') as file:
		csv_reader = csv.reader(file, delimiter='|')
		fields = next(csv_reader)
		for item in csv_reader:
			rows.append(item)

	originals_name = []
	originals_author = []
	with open(f"posts/{a_id}.csv", 'w', encoding='utf-8') as file:
		file.write("")
	with open(f"posts/{a_id}.csv", 'a', encoding='utf-8') as file:
		csv_writer = csv.writer(file, delimiter='|')
		csv_writer.writerow(fields)
		edited_rows = []
		for i in reversed(rows):
			print(i)
		for row in reversed(rows):
			if len(row)>0:
				if row[0]in originals_name and row[3] in originals_author:
					continue
				edited_rows.append(row)
				originals_name.append(row[0])
				originals_author.append(row[3])
		for row in reversed(edited_rows):
			file.write('\n')
			csv_writer.writerow(row)



def get_collection(name: str)-> list:
	file_name = f"art_collections/{name}.csv"
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
def collection_append(collection_name: str, name: str, description: str, author: str, url: str):
	row = [name.replace('|', ' ').replace('\n','&')
		, description.replace('|', ' ').replace('\n','&')
		,author.replace('|', ' ').replace('\n','&')
		,url.replace('|', ' ').replace('\n','&')]
	with open(f"art_collections/{collection_name}.csv", 'a', encoding='utf-8') as file:
		file.write('\n')
		csv_writer = csv.writer(file, delimiter='|')
		csv_writer.writerow(row)


def post_append(account: str | int, title, description, img_url,author_id):
	if not os.path.exists(f"posts/{account}.csv"):
		with open(f"posts/{account}.csv", 'w') as file:
			file.write("title|description|img_url|author")
	with open(f"posts/{account}.csv", 'a', encoding='utf-8') as file:
		row = [title.replace('|', ' ').replace('\n', '&')
			, description.replace('|', ' ').replace('\n', '&')
			, img_url.replace('|', ' ').replace('\n', '&')
			, author_id
			, datetime.datetime.now().timestamp()]

		file.write('\n')
		csv_writer = csv.writer(file, delimiter='|')
		csv_writer.writerow(row)
	posts_edit(account)


def get_posts(a_id: str | int)-> list:

	if not os.path.exists(f"posts/{a_id}.csv"):
		return []
	file_name = f"posts/{a_id}.csv"
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

