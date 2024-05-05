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

radio_channel_id = 1208129687231008808

class AlbumSongs(discord.ui.View):
	def __init__(self,songs_list: typing.List[str], current_play: str, *args, **kwargs):
		self.current_play = current_play
		self.songs_list = songs_list
		super().__init__(*args)

	# Create a class called MyView that subclasses discord.ui.View
	@discord.ui.button(label="Список треків в альбомі:", style=discord.ButtonStyle.blurple, emoji="📋") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button, interaction):
		embed = discord.Embed(title='Наступні треки в альбомі:')
		embed.description=''
		for song in self.songs_list:
			embed.description+=f'- {"▶️ " if self.current_play==song else ""}{song}\n'
		await interaction.response.send_message(embed=embed,ephemeral=True) # Send a message when the button is clicked


def get_song_list(url: str):


	r_onlineradio = requests.get(url).content

	soup = BeautifulSoup(r_onlineradio, 'html.parser')

	song_names = [heading.text for heading in
					 soup.find_all('span', class_='ListRowTitle__LineClamp-sc-1xe2if1-0 jjpOuK')]

	return song_names

class RadioUa(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@commands.Cog.listener()
	async def on_voice_state_update(self,member:discord.Member, before, after):


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
			admin_logs = await voice_channel.guild.fetch_channel(1208129687067303940)
			# noinspection PyTypeChecker
			afk_radio:  discord.VoiceChannel = await self.bot.fetch_channel(1235991951547961478)
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

								if k==album_name:
									embed2.description+=(f"??? <t:{round(v.timestamp())}:T>\n")
							embed2.set_footer(text='Між кожним альбомом грають 2 випадкових сингла')

							await msg.delete()
							msg = await voice_channel.send(embeds=[embed_info,embed2],view=AlbumSongs(songs_list=songs_list,current_play=song_name,timeout=None))

							sde_achievement_list = []

							if audio_info.title=='Sex, Drugs, Etc.':
								for member in voice_channel.members:
									sde_achievement_list.append(member)

							if len(voice_channel.members)<2 and voice_channel.guild.voice_client != None:
								await voice_channel.guild.voice_client.disconnect(force=True)




							if len(members_ids(voice_channel.members))==0 and voice_client.channel!=afk_radio:
								voice_client: discord.VoiceClient = await afk_radio.connect(reconnect=True)
							elif voice_client.channel!=voice_channel:
								voice_client: discord.VoiceClient = await voice_channel.connect(reconnect=True)

							await self.bot.change_presence(status=discord.Status.streaming,
								activity=discord.Activity(type=discord.ActivityType.listening,url="https://discord.com/channels/1208129686031310848/1208129687231008808", name=f"{audio_info.title} - {audio_info.artist} | ({albums_names[album_name]})"))
							await voice_client.play(audio_source, wait_finish=True)


							if audio_info.title=='Sex, Drugs, Etc.':
								for member in voice_channel.members:
									sde_achievement_list.append(member)

								achievements = account_controll.all_achievements()

								for member in sde_achievement_list:
									account_controll.add_to_member('sde', member.id)
									if member.can_send() and member.id != 1221403700115800164:
										await member.send(f"Адміністрація серверу Dev is Art додала вам 1 нових ачівок:\n- **`{achievements['sde']['name']}`**\n> {achievements['sde']['description']}")
						except:
							await admin_logs.send(f"Помилка при завантажені трека: {song_name} ({albums_names[album_name]})")
							continue

def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(RadioUa(bot))  # add the cog to the bot