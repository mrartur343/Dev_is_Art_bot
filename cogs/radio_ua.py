import math
import datetime
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
	async def on_ready(self):
		print("Radio: ON")

		album_short_names = [f for f in listdir('songs')]



		songs = {}

		albums_names = {
			"AM": "AM",
			"MemoryBank": "Memory Bank",
			'Zero': '0',
			'FWN': 'Favourite Worst Nightmare',
			'PS': 'Pineapple Sunrise',
			"ILY": "I Love You.",
			"LDA": "Little Dark Age"
		}

		albums_url = {
			'AM':'https://open.spotify.com/album/78bpIziExqiI9qztvNFlQu',
			'MemoryBank': "https://open.spotify.com/album/08kV4nhdlCBbCWt9fO6AAa",
			'Zero': 'https://open.spotify.com/album/4G3ZBFg8MpTSDxDQ3m2BCb',
			"FWN": 'https://open.spotify.com/album/1XkGORuUX2QGOEIL4EbJKm',
			"PS": "https://open.spotify.com/album/7gA8QSNSZvHUYC9feFpeLj",
			'ILY':'https://open.spotify.com/album/4xkM0BwLM9H2IUcbYzpcBI',
			'LDA': 'https://open.spotify.com/album/7GjVWG39IOj4viyWplJV4H'
		}



		song_files = {}

		for short_name in album_short_names:
			song_files[short_name] = [f for f in listdir(f"songs/{short_name}") if isfile(join(f"songs/{short_name}", f))]






		voice_channel: discord.VoiceChannel = await self.bot.fetch_channel(1208129687231008808)

		voice_client: discord.VoiceClient = await voice_channel.connect()

		for short_name in album_short_names:
			songs[short_name]={}


		for short_name in album_short_names:

			for song_file in song_files[short_name]:
				audio = TinyTag.get(f"songs/{short_name}/{song_file}")
				songs[short_name][audio.title] = song_file

		song_lists = {}

		for short_name in album_short_names:
			song_lists[short_name] = get_song_list(albums_url[short_name])
		album_durations={}
		for k,v in songs.items():
			d = 0
			for name, file in v.items():
				audio_info = TinyTag.get(f"songs/{k}/{file}")
				d+=audio_info.duration
			album_durations[k]=round(d)
		msg = await voice_channel.send(embeds=[discord.Embed(title='load...'),discord.Embed(title='load...')])
		album_list = []
		print(song_lists)
		for album_name in song_lists.keys():
			album_list.append(album_name)


		while True:
			i=0
			for album_name, songs_list in song_lists.items():
				i+=1
				album_start_time = datetime.datetime.now()
				for song_name in songs_list:
					if song_name in songs[album_name]:
						file_name = songs[album_name][song_name]
						audio_source = discord.FFmpegPCMAudio(f"songs/{album_name}/{file_name}")
						audio_info = TinyTag.get(f"songs/{album_name}/{file_name}")

						embed_info = discord.Embed(title='Зараз грає:')

						embed_info.add_field(name="🎵 Назва:", value=audio_info.title)
						embed_info.add_field(name="🧑‍🎤 Виконавець: ", value=audio_info.artist)
						embed_info.add_field(name="⌛ Рік випуску: ", value=audio_info.year)
						embed_info.add_field(name="📡 Бітрейт:", value=str(audio_info.bitrate) + " kBits/s")
						embed_info.add_field(name="⚖️ Розмір: ",
											 value=str(round(audio_info.filesize / (1024 ** 2), 2)) + " mb")
						embed_info.add_field(name="💿 Альбом: ", value=albums_names[album_name])
						embed_info.add_field(name="⏲️ Тривалість: ",
											 value=f"{math.floor(audio_info.duration / 60)}m {math.floor(audio_info.duration) % 60}s")

						embed2 = discord.Embed(title='Розпорядок наступних альбомів')
						embed2.description=''

						timetable = radio_timetable.get_album_times(list(album_durations.keys()), list(album_durations.values()), album_name,album_start_time+ datetime.timedelta(seconds=album_durations[album_name]))
						i=0
						for k, v in timetable.items():
							embed2.description+=(f"{albums_names[k]} <t:{round(v.timestamp())}:T>\n")
							i+=1

						await msg.delete()
						msg = await voice_channel.send(embeds=[embed_info,embed2])

						sde_achievement_list = []

						if audio_info.title=='Sex, Drugs, Etc.':
							for member in voice_channel.members:
								sde_achievement_list.append(member)

						await voice_client.play(audio_source, wait_finish=True)

						if audio_info.title=='Sex, Drugs, Etc.':
							for member in voice_channel.members:
								sde_achievement_list.append(member)

							achievements = account_controll.all_achievements()

							for member in sde_achievement_list:
								account_controll.add_to_member('sde', member.id)
								if member.can_send() and member.id != 1231689822746181806:
									await member.send(f"Адміністрація серверу Dev is Art додала вам 1 нових ачівок:\n- **`{achievements['sde']['name']}`**\n> {achievements['sde']['description']}")



def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(RadioUa(bot))  # add the cog to the bot