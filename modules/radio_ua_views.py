import datetime
import json
import typing
from os import listdir
from os.path import isfile, join

import discord
from discord.ext import pages
from tinytag import TinyTag


radio_bot_list = ['Alpha','Beta','Gamma','Delta']


with open("other/radio_sleep_timers.json", 'r') as file:
	radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())
with open("other/songs_lists_cache.json", 'r') as file:
	songs_lists_cache = json.loads(file.read())
with open("other/albums_images_cache.json", 'r') as file:
	albums_images_cache = json.loads(file.read())
class AlbumSongs(discord.ui.View):
	def __init__(self,  current_play: str, current_album: str, timeout: float | None,
	             timetable: typing.Dict[str, datetime.datetime], next_cycle_time: datetime.datetime,
	             cycle_duration: float, e_pages=typing.List[discord.Embed], *args, **kwargs):
		self.cycle_duration = cycle_duration
		self.next_cycle_time = next_cycle_time
		self.timetable = timetable
		self.current_album = current_album
		self.current_play = current_play
		super().__init__(timeout=timeout, *args)

	# Create a class called MyView that subclasses discord.ui.View

	@discord.ui.button(label="До обраних", style=discord.ButtonStyle.gray,
	                   emoji="❤️")  # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback2(self, button, interaction: discord.Interaction):

		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		if not interaction.user.id in album_likes[self.current_album]:
			album_likes[self.current_album].append(interaction.user.id)
		with open("other/album_likes.json", 'w') as file:
			json.dump(album_likes, file)
		await interaction.response.send_message(
			f"Успішно додано альбом до ваших обраних, тепер вам буде приходити оповіщення за деякий час до початку цього альбому!",
			ephemeral=True, view=DislikeAlbum(liked_album=self.current_album,
			                                  timeout=None))  # Send a message when the button is clicked

	@discord.ui.button(label="Список обраних", style=discord.ButtonStyle.gray,
	                   emoji="💕")  # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback3(self, button, interaction: discord.Interaction):

		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		with open('other/albums_data.json', 'r') as file:
			album_data_json = json.loads(file.read())
		albums_names = {}
		for short_name, info in album_data_json.items():
			albums_names[short_name] = info[0]
		albums_list = []

		for album_name, members in album_likes.items():
			if interaction.user.id in members:
				albums_list.append(album_name)

		dict_timetable = {}
		for line in self.timetable:
			if not line[0] in dict_timetable:
				dict_timetable[line[0]] = line[1]

		def sort_albums(album_key):
			if album_key in dict_timetable:
				return dict_timetable[album_key].timestamp()
			else:
				return 9999999999

		albums_list.sort(key=sort_albums)
		items_pages = []
		for album_name in albums_list:

			time_check = False

			if album_name in dict_timetable:
				album_start_time = dict_timetable[album_name]
				time_check = True
			else:
				album_start_time = self.next_cycle_time

			items_embed = discord.Embed(title=albums_names[album_name])
			n = '\n'
			items_embed.description = f"❤️ | Цей альбом обрали: **{len(album_likes[album_name])}**"

			if time_check:
				items_embed.add_field(name=f'Заграє на радіо:', value=f"<t:{round(album_start_time.timestamp())}:f>")
			else:
				items_embed.add_field(name=f'Заграє на радіо:',
				                      value=f"~ <t:{round(album_start_time.timestamp())}:f> - <t:{round((album_start_time + datetime.timedelta(seconds=self.cycle_duration)).timestamp())}:f> (Цей альбом заграє вже у наступному циклі, тому час лише приблизний)")

			with open('other/notifications_off.json', 'r') as file:
				notifications_off: typing.Dict[str, typing.List[str]] = json.loads(file.read())
				if str(interaction.user.id) in notifications_off:
					if album_name in notifications_off[str(interaction.user.id)]:
						items_embed.add_field(name='Сповіщення про увімкнення:', value='🌙 Вимкнуто')
					else:
						items_embed.add_field(name='Сповіщення про увімкнення:', value='🔔 Увімкнуто')
				else:
					items_embed.add_field(name='Сповіщення про увімкнення:', value='🔔 Увімкнуто')

			if album_name in albums_images_cache:
				items_embed.set_image(url=albums_images_cache[album_name])
			items_embed.set_footer(text=album_name)

			items_pages.append(items_embed)

		buttons = [
			pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
			pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
			pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
			pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
			pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
		]

		paginator: pages.Paginator = pages.Paginator(
			pages=items_pages,
			show_indicator=True,
			use_default_buttons=False,
			custom_buttons=buttons

		)

		pmsg = await paginator.respond(interaction, ephemeral=True)
		custom_view = DislikeAlbumFromList(pmsg.id, pmsg.channel)
		await paginator.update(custom_view=custom_view)

	@discord.ui.button(label="Таймер сну", style=discord.ButtonStyle.gray,
	                   emoji="🌙")  # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback4(self, button, interaction: discord.Interaction):
		view = SleepTimer()
		cancel_check = False

		with open("other/radio_sleep_timers.json", 'r') as file:
			radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())
		for k, v in radio_sleep_timers.items():
			if interaction.user.id in v:
				cancel_check = True

		if cancel_check:
			view.options.insert(0, discord.SelectOption(label='Вимкнути таймер', value='stop'))
		await interaction.respond("Таймер сну автоматично від'єднає вас з голосового каналу тоді, коли вам потрібно:",
		                          view=view, ephemeral=True)


	@discord.ui.button(label="Зупинити радіо", style=discord.ButtonStyle.gray,
	                   emoji="⛔")  # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback5(self, button, interaction: discord.Interaction):
		if interaction.permissions.administrator:
			await interaction.guild.voice_client.disconnect(force=True)
			await interaction.respond("Радіо було вимкнено адміністратором",
		                           ephemeral=True)
		else:
			await interaction.respond("Це може зробити лише адміністратор!",
		                           ephemeral=True)



class RadioPlaylistsView(discord.ui.View):
	def __init__(self,general_radio_ingo_channel,msg_id, *args, **kwargs):
		self.general_radio_ingo_channel: discord.Thread = general_radio_ingo_channel
		self.msg_id: int = msg_id
		super().__init__(timeout=None, *args)

	@discord.ui.button(label="Змінити радіо", style=discord.ButtonStyle.gray,
	                   emoji="📻")
	async def button_callback1(self, button, interaction: discord.Interaction):
		om = interaction.message
		await interaction.respond(f'Переміщення альбому/синглу {om.embeds[0].title}:',
		                          ephemeral=True, view=MoveAlbumToRadio(om.embeds[0].footer.text)) # Send a message when the button is clicked


class MoveAlbumToRadio(discord.ui.View):
	def __init__(self,album_key):
		self.album_key=album_key
		super().__init__(timeout=None)


	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="Виберіть радіо",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		max_values=1,  # the maximum number of values that can be selected by the users
		options=[  # the list of options from which users can choose, a required field
			discord.SelectOption(
				label="Alpha",
				description="Хайперпоп, укр. альт рок | Від @q7d19b_",
				value="Alpha"

			),
			discord.SelectOption(
				label="Beta",
				description="Захід. альт рок, легкий фонк, джаз, інші види захід. року | Від @optymist",
				value="Beta"
			),
			discord.SelectOption(
				label="Gamma",
				description="Андер, важкий фонк, метал | Від @svosvosvosvo",
				value="Gamma"
			),
			discord.SelectOption(
				label="Delta",
				description="OST ігор, джаз, інше спокійне | Від @cap_banana",
				value="Delta"
			)
		]
	)
	async def select_callback(self, select, interaction):  # the function called when the user is done selecting options
		radio_playlists = {}

		for radio_bot in radio_bot_list:
			radio_playlists[radio_bot]= []

		for i in range(4):
			with open('other/radio_playlists.json', 'r') as file:
				radio_playlist: typing.List[str] = json.loads(file.read())[i]
			if select.values[0]!=i:
				if self.album_key in radio_playlist:
					radio_playlist.remove(self.album_key)
			else:
				if not self.album_key in radio_playlist:
					radio_playlist.append(self.album_key)
			radio_playlists[i]=radio_playlist
		with open('other/radio_playlists.json', 'w') as file:
			json.dump(radio_playlists,file)



		await interaction.respond(f"Успішно перенесено цей альбом до радіо {select.values[0]}",ephemeral=True)


class GeneralRadioInfo(discord.ui.View):

	def __init__(self, all_radio_time, *items):
		super().__init__(*items)
		self.all_radio_time = all_radio_time
		self.timeout=None

	@discord.ui.button(label="Всі альбоми/сингли", style=discord.ButtonStyle.gray, emoji="📜")
	async def all_albums_singles(self, button, interaction: discord.Interaction):
		radio_playlists_groups: typing.List[pages.PageGroup] = []

		with open('other/albums_data.json', 'r') as file:
			album_data_json_nf: typing.Dict = json.loads(file.read())

		for i, radio_name in enumerate(radio_bot_list):

			with open('other/radio_playlists.json', 'r') as file:
				radio_playlist = json.loads(file.read())[str(i + 1)]
			with open('other/albums_images_cache.json', 'r') as file:
				album_images_cache = json.loads(file.read())
			with open('other/songs_lists_cache.json', 'r') as file:
				songs_lists_cache = json.loads(file.read())
			with open('other/singles_names.json', 'r') as file:
				singles_names = json.loads(file.read())

			album_data_json = {}
			for ak, ad in album_data_json_nf.items():
				if ak in radio_playlist:
					album_data_json[ak] = ad

			radio_pages: typing.List[pages.Page] = []
			print(album_data_json)
			print(len(album_data_json.values()))
			all_time = 0
			for k in album_data_json.keys():
				d = 0
				for file in [f for f in listdir(f"songs/{k}") if
				             isfile(join(f"songs/{k}", f))]:
					audio_info = TinyTag.get(f"songs/{k}/{file}")
					if audio_info.duration != None:
						d += audio_info.duration
				all_time += d

			for k, v in album_data_json.items():
				embed = discord.Embed(title=v[0])
				if k in album_images_cache:
					embed.set_image(url=album_images_cache[k])
				embed.url = v[1]
				if v[1] in songs_lists_cache:
					embed.description = ''
					for song_name in songs_lists_cache[v[1]]:
						embed.description += f"> - {song_name}\n"

				embed.set_footer(
					text=k)
				radio_pages.append(pages.Page(embeds=[embed]))

			print(f'radio_pages: {len(radio_pages)}')

			radio_group = pages.PageGroup(
				radio_pages,
				label=radio_name

			)
			radio_playlists_groups.append(radio_group)

		print(f'radio_playlists_groups: {len(radio_playlists_groups)}')

		radio_paginator = pages.Paginator(
			pages=radio_playlists_groups,
			timeout=899,
			show_menu=True
		)

		pmsg = await radio_paginator.respond(interaction,ephemeral=True)
		custom_v =RadioPlaylistsView(pmsg.channel,pmsg.id)
		if not interaction.user.id in [658217734814957578, 1154105417283150034, 499940320088293377, 767783132031352884]:
			custom_v.disable_all_items()
		for i in range(4):
			radio_playlists_groups[i].custom_view=custom_v

		await radio_paginator.update(pages=radio_playlists_groups,custom_view=custom_v)



class SleepTimer(discord.ui.View):
	options = []
	options.append(discord.SelectOption(label='15 хв', value='15m'))
	options.append(discord.SelectOption(label='30 хв', value='30m'))
	options.append(discord.SelectOption(label='45 хв', value='45m'))
	options.append(discord.SelectOption(label='60 хв', value='60m'))
	options.append(discord.SelectOption(label='По закінченню трека', value='song_end'))
	options.append(discord.SelectOption(label='По закінченню альбому', value='album_end'))

	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="Вибрати дію",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		max_values=1,  # the maximum number of values that can be selected by the users
		options=options
	)
	async def select_callback(self, select: discord.ui.Select,
	                          interaction: discord.Interaction):  # the function called when the user is done selecting options

		with open("other/radio_sleep_timers.json", 'r') as file:
			radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())


		for k, v in radio_sleep_timers.items():
			if interaction.user.id in v:
				radio_sleep_timers[k].remove(interaction.user.id)
				if k.endswith('m'):
					if len(v) == 0:
						del (radio_sleep_timers[k])
		if select.values[0] == 'stop':
			await interaction.respond(f"Успішно вимкнено таймер сну ☀️", ephemeral=True)


		elif select.values[0].endswith('m'):
			r_timestamp = round(
				(datetime.datetime.now() + datetime.timedelta(minutes=int(select.values[0][:-1]))).timestamp())
			radio_sleep_timers[f"{r_timestamp}m"] = []
			radio_sleep_timers[f"{r_timestamp}m"].append(interaction.user.id)
			await interaction.respond(
				f"Вас автоматично від'єднає <t:{r_timestamp}:R> (по завершенню трека після закінчення аймеру)",
				ephemeral=True)
		else:
			radio_sleep_timers[select.values[0]].append(interaction.user.id)
			await interaction.respond(
				f"Вас автоматично від'єднає з войса по завершенню {'альбому' if select.values[0] == 'album_end' else 'треку'}",
				ephemeral=True)

		with open("other/radio_sleep_timers.json", 'w') as file:
			json.dump(radio_sleep_timers, file)

		self.disable_all_items()
		await self.message.delete()


class DislikeAlbum(discord.ui.View):
	def __init__(self, liked_album: str, timeout: float | None = None, *args, **kwargs):
		self.liked_album = liked_album
		super().__init__(timeout=timeout, *args)

	@discord.ui.button(label="Зняти з обраних", style=discord.ButtonStyle.gray,
	                   emoji="💔")  # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button, interaction: discord.Interaction):
		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		if interaction.user.id in album_likes[self.liked_album]:
			album_likes[self.liked_album].remove(interaction.user.id)
		with open("other/album_likes.json", 'w') as file:
			json.dump(album_likes, file)
		await interaction.response.send_message(f"Успішно видалено альбом з ваших обраних!",
		                                        ephemeral=True)  # Send a message when the button is clicked


class DislikeAlbumFromList(discord.ui.View):
	def __init__(self, msg_id: int, radio_channel: discord.TextChannel, timeout: float | None = None, *args, **kwargs):
		super().__init__(timeout=timeout, *args)
		self.radio_channel = radio_channel
		self.msg_id = msg_id

	@discord.ui.button(label="Зняти з обраних", style=discord.ButtonStyle.gray,
	                   emoji="💔")  # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button: discord.Button, interaction: discord.Interaction):
		self.pmsg = interaction.message
		self.liked_album = self.pmsg.embeds[0].footer.text
		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		if interaction.user.id in album_likes[self.liked_album]:
			album_likes[self.liked_album].remove(interaction.user.id)
		with open("other/album_likes.json", 'w') as file:
			json.dump(album_likes, file)
		await interaction.respond(content=f"Успішно видалено 1 альбом з ваших обраних!",
		                          ephemeral=True)  # Send a message when the button is clicked

	@discord.ui.button(label="", style=discord.ButtonStyle.gray, custom_id='notification_button',
	                   emoji="🔔")  # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback2(self, button, interaction: discord.Interaction):
		self.pmsg = interaction.message
		self.liked_album = self.pmsg.embeds[0].footer.text
		with open('other/notifications_off.json', 'r') as file:
			album_name = self.liked_album
			str_id = str(interaction.user.id)
			not_check = False
			notifications_off: typing.Dict[str, typing.List[str]] = json.loads(file.read())
			if str(interaction.user.id) in notifications_off:
				if album_name in notifications_off[str(interaction.user.id)]:
					notifications_off[str_id].remove(album_name)
					not_check = True
				else:
					notifications_off[str_id].append(album_name)
			else:
				notifications_off[str_id] = []
				notifications_off[str_id].append(album_name)

		with open('other/notifications_off.json', 'w') as file:
			json.dump(notifications_off, file)

		if not_check:
			await interaction.respond(content=f"🔔 Успішно **увімкнуто** сповіщення для цього альбому!", ephemeral=True)
		else:
			await interaction.respond(content=f"🌙 Успішно **вимкнуто** сповіщення для цього альбому!", ephemeral=True)

