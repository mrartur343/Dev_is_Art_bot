import datetime
import json
import discord

def get_all_events() -> list:
	with open("data/events.json", 'r') as file:
		events = json.loads(file.read())
		return events
def get_all_event_ids() -> list:
	with open("data/events.json", 'r') as file:
		events = json.loads(file.read())

	events_ids = []

	for event in events:
		events_ids.append(event['id'])
	return events_ids

def add_event(event: discord.ScheduledEvent, server_invite: str):
	event_id = event.id
	event_name = event.name
	event_desc = event.description
	event_server_url = server_invite
	event_server_name = event.guild.name
	if not (event.guild.icon is None):
		event_server_img_url = event.guild.icon.url
	else:
		event_server_img_url = ''
	event_created_at = round(event.created_at.timestamp())
	event_time = round(event.start_time.timestamp())
	event_url = event.url
	if not (event.cover is None):
		event_img_url = event.cover.url
	else:
		event_img_url = ''

	event_info_dictionary = {
		"id": event_id,
		"name": event_name,
		'desc': event_desc,
		'server_url': event_server_url,
		'server_name': event_server_name,
		'server_img_url': event_server_img_url,
		'created_at': event_created_at,
		'time': event_time,
		'url': event_url,
		'img_url': event_img_url

	}

	all_events = get_all_events()

	if not (event.id in get_all_event_ids()):
		all_events.append(event_info_dictionary)

	with open('data/events.json', 'w') as file:
		json.dump(all_events,file)

def check_events():
	all_events = get_all_events()

	new_events = []

	for event in all_events:
		if event['time']>(datetime.datetime.now()-datetime.timedelta(hours=1)).timestamp():
			new_events.append(event)

	with open('data/events.json', 'w') as file:
		json.dump(new_events, file)


