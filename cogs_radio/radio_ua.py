import asyncio
import io
import json
import math
import datetime
import random
import typing

import requests
from bs4 import BeautifulSoup
from modules import account_controll, radio_timetable
import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from tinytag import TinyTag



class AlbumSongs(discord.ui.View):
	def __init__(self,songs_list: typing.List[str], current_play: str,current_album:str,timeout:float|None, *args, **kwargs):
		self.current_album = current_album
		self.current_play = current_play
		self.songs_list = songs_list
		super().__init__(timeout=timeout,*args)

	# Create a class called MyView that subclasses discord.ui.View
	@discord.ui.button(label="Список треків в альбомі:", style=discord.ButtonStyle.blurple, emoji="📋") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback1(self, button, interaction):
		embed = discord.Embed(title='Наступні треки в альбомі:')
		embed.description=''
		for song in self.songs_list:
			embed.description+=f'- {"▶️ " if self.current_play==song else ""}{song}\n'
		await interaction.response.send_message(embed=embed,ephemeral=True) # Send a message when the button is clicked
	@discord.ui.button(label="До обраних", style=discord.ButtonStyle.blurple, emoji="❤️") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback2(self, button, interaction: discord.Interaction):

		album_likes = {}
		with open("other/album_likes.json", 'r') as file:
			album_likes = json.loads(file.read())
		if not interaction.user.id in album_likes[self.current_album]:
			album_likes[self.current_album].append(interaction.user.id)
		with open("other/album_likes.json", 'w') as file:
			json.dump(album_likes, file)
		await interaction.response.send_message(f"Успішно додано альбом до ваших обраних, тепер вам буде приходити оповіщення за 30 хв. до початку цього альбому!",ephemeral=True,view=DislikeAlbum(liked_album=self.current_album,timeout=None)) # Send a message when the button is clicked

class DislikeAlbum(discord.ui.View):
	def __init__(self, liked_album:str, timeout=float|None, *args, **kwargs):
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

with open("other/songs_lists_cache.json", 'r') as file:
	songs_lists_cache = json.loads(file.read())

def get_song_list(url: str):
	cache_updated = False
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

class RadioUa(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@discord.slash_command(name= 'liked_albums', description='Список обраних вами альбомів')
	async def liked_albums(self, ctx: discord.ApplicationContext):

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
			if ctx.author.id in members:
				albums_list.append(album_name)

		embed= discord.Embed(title='Обрані вами альбоми:')
		embed.description=''
		for album_name in albums_list:
			embed.description+=f"- `❤️` {albums_names[album_name]}\n"

		embed.colour=discord.Colour.from_rgb(226,85,94)

		await ctx.respond(embed=embed)


	@commands.Cog.listener()
	async def on_voice_state_update(self,member:discord.Member, before, after):



		all_guilds = {}

		with open('other/another_guilds_radio.json', 'r') as file:
			all_guilds = json.loads(file.read())

		if not str(member.guild.id) in all_guilds:
			return

		radio_channel_id = all_guilds[str(member.guild.id)][0]

		try:
			channel: discord.VoiceChannel = after.channel
			if channel.id == radio_channel_id and member.id!=self.bot.user.id:
				guild: discord.Guild = channel.guild
				normal_radio = await guild.fetch_channel(radio_channel_id)
				await (await guild.fetch_member(self.bot.user.id)).move_to(normal_radio)
			print(f'ovsu m: {member.name} b: {before.channel} a: {after.channel}')
		except:
			pass


	@commands.Cog.listener()
	async def on_ready(self):
		async for guild in self.bot.fetch_guilds():
			await self.on_ready_guild(guild)


	async def on_ready_guild(self, guild):

		all_guilds = {}

		with open('other/another_guilds_radio.json', 'r') as file:
			all_guilds = json.loads(file.read())

		if not str(guild.id) in all_guilds:
			return
		radio_channel_id = all_guilds[str(guild.id)][0]
		afk_channel_id = all_guilds[str(guild.id)][1]

		print("Radio: ON")

		albums_imgs = {}




		while True:




			album_short_names = [f for f in listdir('songs')]

			songs = {}
			with open('other/albums_data.json', 'r') as file:
				album_data_json = json.loads(file.read())
			singles_names = []
			with open('other/singles_names.json', 'r') as file:
				singles_names = json.loads(file.read())
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
			voice_channel: discord.VoiceChannel = await self.bot.fetch_channel(radio_channel_id)
			admin_logs = await voice_channel.guild.fetch_channel(afk_channel_id)
			# noinspection PyTypeChecker
			afk_radio:  discord.VoiceChannel = await self.bot.fetch_channel(afk_channel_id)
			voice_client = await voice_channel.connect()


			for short_name in album_short_names:
				songs[short_name] = {}

			for short_name in album_short_names:

				for song_file in song_files[short_name]:
					audio = TinyTag.get(f"songs/{short_name}/{song_file}")
					songs[short_name][audio.title] = song_file

			song_lists = []
			random.shuffle(singles_names)
			random.shuffle(album_short_names)
			for single_name in singles_names:
				if single_name in album_short_names:
					album_short_names.remove(single_name)
			i=0
			album_list = []
			for k,v in albums_url.items():
				print(f"{k} {v}")
			print(album_short_names)
			for short_name in album_short_names:

				song_lists.append([short_name, get_song_list(albums_url[short_name])])
				album_list.append(short_name)
				for _ in range(2):
					if i>=len(singles_names):
						i=0
					song_lists.append([singles_names[i],get_song_list(albums_url[singles_names[i]])])
					album_list.append(singles_names[i])
					i+=1
			album_durations = {}
			for k, v in songs.items():
				d = 0
				for name, file in v.items():
					audio_info = TinyTag.get(f"songs/{k}/{file}")
					if audio_info.duration!=None:
						d += audio_info.duration
				album_durations[k] = round(d)
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
			for album_name, songs_list in song_lists:
				i+=1
				album_start_time = datetime.datetime.now()
				skip_offset=0
				next_index = album_list.index(album_name)
				if next_index==len(album_list):
					next_index=0
				with open("other/album_likes.json", 'r') as file:
					album_likes = json.loads(file.read())
					for user_like in album_likes[album_list[next_index]]:
						user=await self.bot.fetch_user(user_like)
						if user.can_send():
							next_album_timestamp = (album_start_time+datetime.timedelta(seconds=album_durations[album_name])).timestamp()
							await user.send(f"Альбом **`{albums_names[album_list[next_index]]}`**, який ви вподобали, буде у <#{all_guilds[str(guild.id)][0]}> <t:{next_album_timestamp}:R>", view=DislikeAlbum(timeout=None,liked_album=album_name))

				for song_name in songs_list:
					if song_name in songs[album_name]:
						try:
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

							embed_info = discord.Embed(title='Зараз грає:')
							embed_info.set_thumbnail(url=albums_imgs[album_name])

							embed_info.add_field(name="🎵 Назва:", value=audio_info.title)
							embed_info.add_field(name="🧑‍🎤 Виконавець: ", value=audio_info.artist)
							embed_info.add_field(name="⌛ Рік випуску: ", value=audio_info.year)
							embed_info.add_field(name="📡 Бітрейт:", value=str(audio_info.bitrate) + " kBits/s")
							embed_info.add_field(name="⚖️ Розмір: ",
												 value=str(round(audio_info.filesize / (1024 ** 2), 2)) + " mb")
							embed_info.add_field(name="💿 Альбом: " if (not album_name in singles_names) else "Сингл ⚡:", value=albums_names[album_name] if (not album_name in singles_names) else "Між кожним альбомом грають 2 випадкових сингла")
							embed_info.add_field(name="⏲️ Тривалість: ",
												 value=f"{math.floor(audio_info.duration / 60)}m {math.floor(audio_info.duration) % 60}s")

							embed2 = discord.Embed(title='Розпорядок наступних альбомів')
							embed2.description=''
							print('Albums durations\n----')
							print(album_durations)
							print("----")

							timetable = radio_timetable.get_album_times(list(album_list), album_durations, album_name,album_start_time+ datetime.timedelta(seconds=album_durations[album_name]-skip_offset))
							i=0
							for k, v in timetable:
								print(f'k: {k}, v: {v} s: {k in singles_names}')
								if (not k in singles_names) and k!=album_name:
									embed2.description+=(f"<t:{round(v.timestamp())}:t> {albums_names[k]} {f' (<t:{round(v.timestamp())}:R>)' if i==0 else ''}\n")
									if i==7:
										break
									i+=1

							embed2.set_footer(text='Між кожним альбомом грають 2 випадкових сингла')

							await msg.delete()
							msg = await voice_channel.send(embeds=[embed_info,embed2],view=AlbumSongs(songs_list=songs_list,current_play=song_name,timeout=None, current_album=album_name))




							if len(members_ids(voice_channel.members))==0 and voice_client.channel!=afk_radio:
								voice_client: discord.VoiceClient = await afk_radio.connect(reconnect=True)
							elif voice_client.channel!=voice_channel:
								voice_client: discord.VoiceClient = await voice_channel.connect(reconnect=True)

							await self.bot.change_presence(status=discord.Status.streaming,
								activity=discord.Activity(type=discord.ActivityType.listening,url="https://discord.com/channels/1208129686031310848/1208129687231008808", name=f"{audio_info.title} - {audio_info.artist} | ({albums_names[album_name]})"))
							await voice_client.play(audio_source, wait_finish=True)

						except:
							await admin_logs.send(f"Помилка при завантажені трека: {song_name} ({albums_names[album_name]})")
							continue

def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(RadioUa(bot))  # add the cog to the bot