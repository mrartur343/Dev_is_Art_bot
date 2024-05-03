import asyncio
import io
import json
import math
import datetime
import time

import requests
from bs4 import BeautifulSoup
from modules import account_controll, radio_timetable
import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from tinytag import TinyTag

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
		print(f'ovsu m: {member.name} b: {before.channel} a: {after.channel}')


		channel: discord.VoiceChannel = after.channel
		if channel.id == 1208129687231008808 and member.id!=self.bot.user.id:
			guild: discord.Guild = channel.guild
			normal_radio = await guild.fetch_channel(1208129687231008808)
			await (await guild.fetch_member(self.bot.user.id)).move_to(normal_radio)

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


			voice_channel: discord.VoiceChannel = await self.bot.fetch_channel(1208129687231008808)
			afk_radio:  discord.VoiceChannel = await self.bot.fetch_channel(1235991951547961478)
			voice_client = await voice_channel.connect()


			for short_name in album_short_names:
				songs[short_name] = {}

			for short_name in album_short_names:

				for song_file in song_files[short_name]:
					audio = TinyTag.get(f"songs/{short_name}/{song_file}")
					songs[short_name][audio.title] = song_file

			song_lists = {}
			for single_name in singles_names:
				if single_name in album_short_names:
					album_short_names.remove(single_name)
			i=0
			for short_name in album_short_names:
				song_lists[short_name] = get_song_list(albums_url[short_name])
				for _ in range(2):
					if i>=len(singles_names):
						i=0
					song_lists[singles_names[i]] = get_song_list(albums_url[short_name])
			album_durations = {}
			for k, v in songs.items():
				d = 0
				for name, file in v.items():
					audio_info = TinyTag.get(f"songs/{k}/{file}")
					print(f"get: songs/{k}/{file}")
					if audio_info.duration!=None:
						d += audio_info.duration
				album_durations[k] = round(d)
			msg = await voice_channel.send(embeds=[discord.Embed(title='load...'), discord.Embed(title='load...')])
			album_list = []
			print(song_lists)
			for album_name in song_lists.keys():
				album_list.append(album_name)


			####

			i=0
			for album_name, songs_list in song_lists.items():
				i+=1

				album_start_time = datetime.datetime.now()
				skip_offset=0
				for song_name in songs_list:
					if song_name in songs[album_name]:
						print(voice_channel.members)
						file_name = songs[album_name][song_name]
						audio_source = discord.FFmpegPCMAudio(f"songs/{album_name}/{file_name}")
						audio_info = TinyTag.get(f"songs/{album_name}/{file_name}", image=True)

						if not album_name in albums_imgs:
							image_data: bytes = audio_info.get_image()
							with open('a.png', 'wb') as file:
								file.write(image_data)

							file = discord.File(fp='a.png')
							admin_logs = await voice_channel.guild.fetch_channel(1208129687067303940)
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

						timetable = radio_timetable.get_album_times(list(album_durations.keys()), list(album_durations.values()), album_name,album_start_time+ datetime.timedelta(seconds=album_durations[album_name]-skip_offset))
						i=0
						for k, v in timetable.items():
							if not k in singles_names:
								embed2.description+=(f"{albums_names[k]} <t:{round(v.timestamp())}:T>\n")
								i+=1
						embed2.set_footer(text='Між кожним альбомом грають 2 випадкових сингла')

						await msg.delete()
						msg = await voice_channel.send(embeds=[embed_info,embed2])

						sde_achievement_list = []

						if audio_info.title=='Sex, Drugs, Etc.':
							for member in voice_channel.members:
								sde_achievement_list.append(member)

						if len(voice_channel.members)<2 and voice_channel.guild.voice_client != None:
							await voice_channel.guild.voice_client.disconnect(force=True)


						def members_ids(members):
							r = [m.id for m in members]
							if self.bot.user.id in r:
								r.remove(self.bot.user.id)
							return r

						if len(members_ids(voice_channel.members))==0:
							voice_client: discord.VoiceClient = await afk_radio.connect(reconnect=False)
						else:
							voice_client: discord.VoiceClient = await voice_channel.connect(reconnect=False)

						await voice_client.play(audio_source, wait_finish=True)


						if audio_info.title=='Sex, Drugs, Etc.':
							for member in voice_channel.members:
								sde_achievement_list.append(member)

							achievements = account_controll.all_achievements()

							for member in sde_achievement_list:
								account_controll.add_to_member('sde', member.id)
								if member.can_send() and member.id != 1221403700115800164:
									await member.send(f"Адміністрація серверу Dev is Art додала вам 1 нових ачівок:\n- **`{achievements['sde']['name']}`**\n> {achievements['sde']['description']}")



def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(RadioUa(bot))  # add the cog to the bot