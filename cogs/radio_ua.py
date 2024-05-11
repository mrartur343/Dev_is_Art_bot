import asyncio
import json
import math
import datetime
import random

import jmespath
import typing

import requests
from bs4 import BeautifulSoup
from modules import account_controll, radio_timetable
import discord
from discord.ext import commands, pages
from os import listdir
from os.path import isfile, join
from tinytag import TinyTag

radio_channel_id = 1208129687231008808

class AlbumSongs(discord.ui.View):
	def __init__(self,songs_list: typing.List[str], current_play: str,current_album:str,timeout:float|None,timetable: typing.Dict[str,datetime.datetime],next_cycle_time:datetime.datetime, cycle_duration: float, *args, **kwargs):
		self.cycle_duration = cycle_duration
		self.next_cycle_time = next_cycle_time
		self.timetable = timetable
		self.current_album = current_album
		self.current_play = current_play
		self.songs_list = songs_list
		super().__init__(timeout=timeout,*args)

	# Create a class called MyView that subclasses discord.ui.View
	@discord.ui.button(label="Список треків в альбомі:", style=discord.ButtonStyle.gray, emoji="📋") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback1(self, button, interaction):
		embed = discord.Embed(title='Наступні треки в альбомі:')
		embed.description=''
		for song in self.songs_list:
			embed.description+=f'- {"▶️ " if self.current_play==song else ""}{song}\n'
		await interaction.response.send_message(embed=embed,ephemeral=True) # Send a message when the button is clicked
	@discord.ui.button(label="До обраних", style=discord.ButtonStyle.gray, emoji="❤️") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback2(self, button, interaction: discord.Interaction):

		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		if not interaction.user.id in album_likes[self.current_album]:
			album_likes[self.current_album].append(interaction.user.id)
		with open("other/album_likes.json", 'w') as file:
			json.dump(album_likes, file)
		await interaction.response.send_message(f"Успішно додано альбом до ваших обраних, тепер вам буде приходити оповіщення за 30 хв. до початку цього альбому!",ephemeral=True,view=DislikeAlbum(liked_album=self.current_album,timeout=None)) # Send a message when the button is clicked
	@discord.ui.button(label="Список обраних", style=discord.ButtonStyle.gray, emoji="💕") # Create a button with the label "😎 Click me!" with color Blurple
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
			dict_timetable[line[0]]=line[1]
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
				items_embed.add_field(name=f'Заграє на радіо:',value=f"<t:{round(album_start_time.timestamp())}:f>")
			else:
				items_embed.add_field(name=f'Заграє на радіо:',value=f"~ <t:{round(album_start_time.timestamp())}:f> - <t:{round((album_start_time+datetime.timedelta(seconds=self.cycle_duration)).timestamp())}:f> (Цей альбом заграє вже у наступному циклі, тому час лише приблизний)")

			with open('other/notifications_off.json', 'r') as file:
				notifications_off: typing.Dict[str,typing.List[str]] = json.loads(file.read())
				if str(interaction.user.id) in notifications_off:
					if album_name in notifications_off[str(interaction.user.id)]:
						items_embed.add_field(name='Сповіщення про увімкнення:', value='🌙 Вимкнуто')
					else:
						items_embed.add_field(name='Сповіщення про увімкнення:',value='🔔 Увімкнуто')
				else:
					items_embed.add_field(name='Сповіщення про увімкнення:',value='🔔 Увімкнуто')

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

		msg = await paginator.respond(interaction,ephemeral=True)
		custom_view = DislikeAlbumFromList(msg)
		await paginator.update(custom_view=custom_view)

class DislikeAlbum(discord.ui.View):
	def __init__(self, liked_album:str, timeout:float|None=None, *args, **kwargs):
		self.liked_album = liked_album
		super().__init__(timeout=timeout,*args)

	@discord.ui.button(label="Зняти з обраних", style=discord.ButtonStyle.gray, emoji="💔") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button, interaction: discord.Interaction):

		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		if interaction.user.id in album_likes[self.liked_album]:
			album_likes[self.liked_album].remove(interaction.user.id)
		with open("other/album_likes.json", 'w') as file:
			json.dump(album_likes, file)
		await interaction.response.send_message(f"Успішно видалено альбом з ваших обраних!",ephemeral=True) # Send a message when the button is clicked

class DislikeAlbumFromList(discord.ui.View):
	def __init__(self,msg:discord.Message, timeout:float|None=None, *args, **kwargs):
		super().__init__(timeout=timeout,*args)
		self.msg = msg
		self.liked_album = self.msg.embeds[0].footer.text

	@discord.ui.button(label="Зняти з обраних", style=discord.ButtonStyle.gray, emoji="💔") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button, interaction: discord.Interaction):

		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		if interaction.user.id in album_likes[self.liked_album]:
			album_likes[self.liked_album].remove(interaction.user.id)
		with open("other/album_likes.json", 'w') as file:
			json.dump(album_likes, file)
		await self.msg.edit(content=f"Успішно видалено 1 альбом з ваших обраних!",embeds=[],view=None) # Send a message when the button is clicked
	@discord.ui.button(label="", style=discord.ButtonStyle.gray,custom_id='notification_button', emoji="🔔") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback2(self, button, interaction: discord.Interaction):
		with open('other/notifications_off.json', 'r') as file:
			album_name = self.liked_album
			str_id = str(interaction.user.id)
			not_check = False
			notifications_off: typing.Dict[str, typing.List[str]] = json.loads(file.read())
			if str(interaction.user.id) in notifications_off:
				if album_name in notifications_off[str(interaction.user.id)]:
					notifications_off[str_id].remove(album_name)
					not_check=True
				else:
					notifications_off[str_id].append(album_name)
			else:
				notifications_off[str_id]=[]
				notifications_off[str_id].append(album_name)


		with open('other/notifications_off.json', 'w') as file:
			json.dump(notifications_off, file)

		if not_check:
			await self.msg.edit(content=f"🔔 Успішно **увімкнуто** сповіщення для цього альбому!",embeds=[],view=None)
		else:
			await self.msg.edit(content=f"🌙 Успішно **вимкнуто** сповіщення для цього альбому!",embeds=[],view=None)


with open("other/songs_lists_cache.json", 'r') as file:
	songs_lists_cache = json.loads(file.read())
with open("other/albums_images_cache.json", 'r') as file:
	albums_images_cache = json.loads(file.read())

def get_song_list(url: str):
	global songs_lists_cache

	if url in songs_lists_cache:
		return songs_lists_cache[url]
	else:
		r_onlineradio = requests.get(url).content

		soup = BeautifulSoup(r_onlineradio, 'html.parser')

		song_names = [heading.text for heading in
						 soup.find_all('span', class_='ListRowTitle__LineClamp-sc-1xe2if1-0 jjpOuK')]
		songs_lists_cache[url]=song_names
		with open('other/songs_lists_cache.json', 'w') as file:
			json.dump(songs_lists_cache, file)
		return song_names
def get_album_name_and_key(url: str):
	r_onlineradio = requests.get(url).content

	soup = BeautifulSoup(r_onlineradio, 'html.parser')

	album_name = [heading.text for heading in
						 soup.find_all('h1', class_='Type__TypeElement-sc-goli3j-0 ofaEA gj6rSoF7K4FohS2DJDEm')][0]
	album_key = url[31:]
	return (album_name,album_key)

class RadioUa(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot



	@discord.slash_command(name="playlist_toggle", description='Лише для адмінів')
	@commands.has_permissions(administrator=True)
	async def playlist_toggle(self,ctx: discord.ApplicationContext,key_name:discord.Option(str), toggle: discord.Option(bool)):

		with open('other/playlists_names.json', 'r') as file:
			playlists_names = json.loads(file.read())

		if toggle and (not key_name in playlists_names):
			playlists_names.append(key_name)
		elif (not toggle ) and (key_name in playlists_names):
			playlists_names.remove(key_name)

		await ctx.respond(f'Успішно зміненно {key_name} у  playlists_names на {toggle}')

	@commands.Cog.listener()
	async def on_voice_state_update(self,member:discord.Member, before, after):


		try:
			achannel: discord.VoiceChannel = after.channel
			bchannel: discord.VoiceChannel = after.channel

			if not (achannel is None):
				achannel_id = achannel.id
			else:
				achannel_id = 0

			if not (bchannel is None):
				bchannel_id = bchannel.id
			else:
				bchannel_id = 0

			if member.id!=self.bot.user.id:
				if achannel_id == radio_channel_id:
					guild: discord.Guild = achannel.guild
					normal_radio = await guild.fetch_channel(radio_channel_id)
					await (await guild.fetch_member(self.bot.user.id)).move_to(normal_radio)
				elif bchannel_id == radio_channel_id and achannel_id != radio_channel_id:
					guild: discord.Guild = bchannel.guild
					afk_radio = await guild.fetch_channel(1235991951547961478)
					await (await guild.fetch_member(self.bot.user.id)).move_to(afk_radio)


			print(f'ovsu m: {member.name} b: {before.channel} a: {after.channel}')
		except:
			pass

	@commands.Cog.listener()
	async def on_ready(self):
		print("Radio: ON")

		albums_imgs=albums_images_cache
		start_check = True

		voice_channel: discord.VoiceChannel = await self.bot.fetch_channel(radio_channel_id)
		voice_client = await voice_channel.connect(reconnect=True)



		async for message in voice_channel.history():
			if message.author.id == self.bot.user.id:
				await message.delete()

		while True:


			album_short_names = [f for f in listdir('songs')]

			songs = {}
			with open('other/albums_data.json', 'r') as file:
				album_data_json = json.loads(file.read())
			singles_names = []
			with open('other/singles_names.json', 'r') as file:
				singles_names = json.loads(file.read())
			playlists_names = []
			with open('other/playlists_names.json', 'r') as file:
				playlists_names = json.loads(file.read())
			albums_names={}
			albums_url={}
			for short_name, info in album_data_json.items():
				albums_names[short_name]=info[0]
				albums_url[short_name] = info[1]
			song_files = {}

			for short_name in album_short_names:
				song_files[short_name] = [f for f in listdir(f"songs/{short_name}") if
										  isfile(join(f"songs/{short_name}", f))]

			# noinspection PyTypeChecker


			admin_logs = await voice_channel.guild.fetch_channel(1208129687067303940)
			# noinspection PyTypeChecker
			afk_radio:  discord.VoiceChannel = await self.bot.fetch_channel(1235991951547961478)
			await admin_logs.send(f'Cycle {datetime.datetime.now().strftime(format="%c")}')
			if start_check:
				await admin_logs.send("## (start)")
				start_check=False

			for short_name in album_short_names:
				songs[short_name] = {}

			for short_name in album_short_names:

				for song_file in song_files[short_name]:
					audio = TinyTag.get(f"songs/{short_name}/{song_file}")
					songs[short_name][audio.title] = song_file
			album_durations = {}
			for k, v in songs.items():
				d = 0
				for name, file in v.items():
					audio_info = TinyTag.get(f"songs/{k}/{file}")
					if audio_info.duration!=None:
						d += audio_info.duration
				album_durations[k] = round(d)

			song_lists = []
			random.shuffle(singles_names)
			random.shuffle(album_short_names)
			random.shuffle(playlists_names)
			for single_name in singles_names:
				if single_name in album_short_names:
					album_short_names.remove(single_name)
			for playlist_name in playlists_names:
				if playlist_name in album_short_names:
					album_short_names.remove(playlists_names)
			i=0
			album_list = []
			st = 0.0

			j = 0


			for short_name in album_short_names:


				if (st/3600)>8:
					if j>=len(playlists_names):
						song_lists.append([playlists_names[j],get_song_list(albums_url[playlists_names[j]])])
					j+=1
				st += album_durations[short_name]
				song_lists.append([short_name, get_song_list(albums_url[short_name])])
				album_list.append(short_name)
				for _ in range(2):
					if i>=len(singles_names):
						i=0
					st += album_durations[singles_names[i]]
					song_lists.append([singles_names[i],get_song_list(albums_url[singles_names[i]])])
					album_list.append(singles_names[i])
					i+=1
			cycle_duration = 0.0
			msg = await voice_channel.send(embeds=[discord.Embed(title='load...'), discord.Embed(title='load...')])

			album_likes={}
			with open("other/album_likes.json", 'r') as file:
				album_likes = json.loads(file.read())
			for album in album_list:
				if not album in album_likes:
					album_likes[album]=[]
			with open("other/album_likes.json", 'w') as file:
				json.dump(album_likes, file)


			####

			i=0

			def members_ids(members):
				r = [m.id for m in members]
				if self.bot.user.id in r:
					r.remove(self.bot.user.id)
				return r
			print("ALBUMS\n-----")
			for album_name, songs_list in song_lists[:10]:
				print(f"**{album_name}**")
				for song in songs_list:
					print(song)
			print()

			for album_name,_ in song_lists:
				cycle_duration+=album_durations[album_name]

			next_cycle_time = datetime.datetime.now()+datetime.timedelta(seconds=cycle_duration)
			await admin_logs.send(f'Cycle duration: {math.floor((cycle_duration/60)/60)} h {math.floor((cycle_duration%3600) /60)} m {math.floor(cycle_duration%60)} s (next cycle: <t:{round(next_cycle_time.timestamp())}:F>)')
			for album_name, songs_list in song_lists:
				i+=1
				album_start_time = datetime.datetime.now()
				next_index = album_list.index(album_name)+3
				if next_index>=len(album_list):
					pass
				elif next_index==0:
					for next_index2 in range(3):
						with open("other/album_likes.json", 'r') as file:
							album_likes = json.loads(file.read())
							for user_like in album_likes[album_list[next_index2]]:
								not_check = True
								with open('other/notifications_off.json', 'r') as file:
									notifications_off: typing.Dict[str, typing.List[str]] = json.loads(file.read())
									if str(user_like) in notifications_off:
										if album_name in notifications_off[str(user_like)]:
											not_check=False

								user=await self.bot.fetch_user(user_like)
								if user.can_send() and not_check:
									next_album_timestamp = (album_start_time+datetime.timedelta(seconds=album_durations[album_name])).timestamp()
									album_notification_label = "Сингл" if album_name in singles_names else "Альбом"
									await user.send(f"{album_notification_label} **`{albums_names[album_list[next_index2]]}`**, який ви вподобали, буде у <#1208129687231008808> <t:{round(next_album_timestamp)}:R>", view=DislikeAlbum(timeout=None,liked_album=album_name))
				else:
					with open("other/album_likes.json", 'r') as file:
						album_likes = json.loads(file.read())
						for user_like in album_likes[album_list[next_index]]:
							user=await self.bot.fetch_user(user_like)
							if user.can_send():
								next_album_timestamp = (album_start_time+datetime.timedelta(seconds=album_durations[album_name])).timestamp()
								album_notification_label = "Сингл" if album_name in singles_names else "Альбом"
								await user.send(f"{album_notification_label} **`{albums_names[album_list[next_index]]}`**, який ви вподобали, буде у <#1208129687231008808> <t:{round(next_album_timestamp)}:R>", view=DislikeAlbum(timeout=None,liked_album=album_name))
				print("---songs_list---")
				print(song_lists)
				print("------")
				for song_name in songs_list:
					if song_name in songs[album_name]:
						try:
							await admin_logs.send(f'Play {song_name} ({album_name}) ({datetime.datetime.now().strftime(format="%c")})')
							print(voice_channel.members)
							file_name = songs[album_name][song_name]
							audio_source = discord.FFmpegPCMAudio(f"songs/{album_name}/{file_name}")
							audio_info = TinyTag.get(f"songs/{album_name}/{file_name}", image=True)

							if not album_name in albums_imgs:
								image_data: bytes = audio_info.get_image()
								with open('a.png', 'wb') as file:
									file.write(image_data)

								file = discord.File(fp='a.png')
								imgmsg = await admin_logs.send(content=".",file=file)
								albums_imgs[album_name] = imgmsg.attachments[0].url
								with open('other/albums_images_cache.json', 'w') as file:
									json.dump(albums_imgs, file)

							embed_info = discord.Embed(title='Зараз грає:')
							embed_info.set_thumbnail(url=albums_imgs[album_name])

							embed_info.add_field(name="🎵 Назва:", value=audio_info.title)
							embed_info.add_field(name="🧑‍🎤 Виконавець: ", value=audio_info.artist)
							embed_info.add_field(name="⌛ Рік випуску: ", value=audio_info.year)
							embed_info.add_field(name="💿 Альбом: " if (not album_name in singles_names) else "Сингл ⚡:", value=albums_names[album_name] if (not album_name in singles_names) else "Між кожним альбомом грають 2 випадкових сингла")
							embed_info.add_field(name="⏲️ Тривалість: ",
												 value=f"{math.floor(audio_info.duration / 60)}m {math.floor(audio_info.duration) % 60}s")
							embed_info.add_field(name="📻 Наступний трек: ",
												 value=f"<t:{round((datetime.datetime.now()+datetime.timedelta(seconds=audio_info.duration)).timestamp())}:R>")

							embed2 = discord.Embed(title='Розпорядок наступних альбомів')
							embed2.description=''
							print('Albums durations\n----')
							print(album_durations)
							print("----")

							timetable = radio_timetable.get_album_times(jmespath.search("[*][0]", song_lists), album_durations, album_name,album_start_time+ datetime.timedelta(seconds=album_durations[album_name]))
							i=0
							single_check=True
							old_emoji = ""
							for k, v in timetable:
								if i<6:
									v: datetime.datetime

									kyiv_h = v.hour
									print(kyiv_h)


									time_emoji = "🏙️" if 12 <= kyiv_h < 18 else (
										"🌇" if 18 <= kyiv_h < 24 else ('🌇' if 6 <= kyiv_h < 12 else "🌃"))
									if time_emoji!=old_emoji:
										embed2.description += f"\n- {time_emoji}\n"
									print(f'k: {k}, v: {v} s: {k in singles_names}')
									if i==0 and (k in singles_names) and single_check:
										single_check=False
										embed2.description+=f"⚡ <t:{round(v.timestamp())}:t> Випадковий сингл (<t:{round(v.timestamp())}:R>)\n"
										embed2.description+="-----\n"
									elif (not k in singles_names) and k!=album_name:
										if k in playlists_names:
											embed2.description +=f'📜 '
										embed2.description+=(f"<t:{round(v.timestamp())}:t> {albums_names[k]} {f' (<t:{round(v.timestamp())}:R>)' if (i == 0) and single_check else ''}{' (плейлист)' if k in playlists_names else ''}\n")
										i+=1

								old_emoji=time_emoji
							if i<6:
								embed2.description += (
									f"<t:{round(next_cycle_time.timestamp())}:t> Наступний цикл (довантаження нових альбомів/синглів/плейлистів) {f' (<t:{round(next_cycle_time.timestamp())}:R>)' if (i == 0) and single_check else ''}\n")
							embed2.set_footer(text='Між кожним альбомом грають 2 випадкових сингла | Раз у ~8 годин грають плейлисти')

							await msg.delete()
							msg = await voice_channel.send(embeds=[embed_info,embed2],view=AlbumSongs(songs_list=songs_list,current_play=song_name,timeout=None, current_album=album_name,timetable=timetable,next_cycle_time=next_cycle_time,cycle_duration=cycle_duration))

							sde_achievement_list = []

							if audio_info.title=='Sex, Drugs, Etc.':
								for member in voice_channel.members:
									sde_achievement_list.append(member)



							if voice_channel.guild.me.voice is None:
								await admin_logs.send("Discord disconect me from voice")
								if len(voice_channel.members)>0:
									voice_client = await voice_channel.connect(reconnect=True)
								else:
									voice_client = await afk_radio.connect(reconnect=True)
							await self.bot.change_presence(status=discord.Status.streaming,
								activity=discord.Activity(type=discord.ActivityType.listening,url="https://discord.com/channels/1208129686031310848/1208129687231008808", name=f"{audio_info.title} - {audio_info.artist} | ({albums_names[album_name]})"))

							try:
								await voice_client.play(audio_source, wait_finish=True)
							except Exception as error_play:
								if error_play.__str__() in ['Not connected to voice.', "Cannot write to closing transport"]:
									try:
										if len(voice_channel.members)>0:
											voice_client = await voice_channel.connect(reconnect=True)
										else:
											voice_client = await afk_radio.connect(reconnect=True)
									except Exception as error_connect:
										if error_connect.__str__()=="Cannot write to closing transport":
											connect_check = True
											while connect_check:
												await admin_logs.send('Try to connect....')
												await asyncio.sleep(5)
												if len(voice_channel.members) > 0:
													voice_client = await voice_channel.connect(reconnect=True)
													connect_check=False
												else:
													voice_client = await afk_radio.connect(reconnect=True)
													connect_check=False

							if audio_info.title=='Sex, Drugs, Etc.':
								for member in voice_channel.members:
									sde_achievement_list.append(member)

								achievements = account_controll.all_achievements()

								for member in sde_achievement_list:
									account_controll.add_to_member('sde', member.id)
									if member.can_send() and member.id != 1221403700115800164:
										await member.send(f"Адміністрація серверу Dev is Art додала вам 1 нових ачівок:\n- **`{achievements['sde']['name']}`**\n> {achievements['sde']['description']}")
						except Exception as error:
							await admin_logs.send(f"Помилка при завантажені трека: {song_name} ({albums_names[album_name]})\n{error}")
							continue

async def setup(bot):  # this is called by Pycord to setup the cog
	await bot.add_cog(RadioUa(bot))  # add the cog to the bot