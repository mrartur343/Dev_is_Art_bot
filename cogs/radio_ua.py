import math
import datetime
import time
from modules import account_controll
import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from tinytag import TinyTag


class RadioUa(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot
		print("Radio: ON")

	@commands.Cog.listener()
	async def on_ready(self):
		songs = {}

		albums_names = {
			"AM": "AM",
			"MemoryBank": "Memory Bank",
			'Zero': '0',
			'FWN': 'Favourite Worst Nightmare',
			'PS': 'Pineapple Sunrise'
		}

		AM_list = [
			'Do I Wanna Know?',
			'R U Mine?',
			"One For The Road",
			'Arabella',
			'I Want It All',
			"No. 1 Party Anthem",
			"Mad Sounds",
			"Fireside",
			"Why'd You Only Call Me When You're High?",
			'Snap Out Of It',
			"Knee Socks",
			"I Wanna Be Yours"

		]

		MemoryBank_list = [
			'Memory Bank',
			'Cepheid Disk',
			'Electrifying Landscape',
			'Blueshift',
			'Far Apart',
			'Lisa',
			'New Touch',
			'Spliff & Wesson',
			'Motions',
			'System Shutdown',
			'Simulation Sunrise(BONUS)',
			'Decades(BONUS)',
			'Last Call(BONUS)'
		]
		Zero_list = [
			'Breathe In',
			'Easy Way Out',
			'Nobody Loves Me Like You',
			'I\'ll Keep Coming',
			'Half Asleep',
			'Please Don\'t Stop (Chapter 1)',
			'I\'m Leaving',
			'In the Morning',
			'Phantoms',
			'Anything You Need',
			'Dreamer',
			'Vampire on My Fridge',
			'Please Don\'t Stop (Chapter 2)',
		]

		FWN_list = [
			"Brianstorm",
			"Teddy Picker",
			"D is for Dangerous",
			"Balaclava",
			"Fluorescent Adolescent",
			"Only Ones Who Know",
			"Do Me a Favour",
			"This House is a Circus",
			"If You Were There, Beware",
			"The Bad Thing",
			"Old Yellow Bricks",
			"505"
		]

		PS_list = [
			'Pineapple Sunrise',
			'High & Driving',
			'Unlovable',
			'Trouble With This Bed',
			'Desert Oasis',
			'Homebody',
			'Hard Feelings',
			'Silent Type',
			'Miss You',
			'Wildfire',
			'Sex, Drugs, Etc.',
		]

		AM = [f for f in listdir("songs/AM") if isfile(join("songs/AM", f))]
		print(AM)

		MemoryBank = [f for f in listdir("songs/MemoryBank") if isfile(join("songs/MemoryBank", f))]
		print(MemoryBank)

		Zero = [f for f in listdir("songs/Zero") if isfile(join("songs/Zero", f))]
		print(Zero)

		FWN = [f for f in listdir("songs/FWN") if isfile(join("songs/FWN", f))]
		print(FWN)

		PS = [f for f in listdir("songs/PS") if isfile(join("songs/PS", f))]
		print(PS)





		voice_channel: discord.VoiceChannel = await self.bot.fetch_channel(1208129687231008808)

		voice_client: discord.VoiceClient = await voice_channel.connect()
		songs = {'AM': {}, 'MemoryBank': {}, 'Zero': {}, 'FWN': {}, 'PS': {}}

		for song_file in AM:
			audio = TinyTag.get(f"songs/AM/{song_file}")
			songs['AM'][audio.title] = song_file
		for song_file in MemoryBank:
			audio = TinyTag.get(f"songs/MemoryBank/{song_file}")
			songs['MemoryBank'][audio.title] = song_file
		for song_file in Zero:
			audio = TinyTag.get(f"songs/Zero/{song_file}")
			songs['Zero'][audio.title] = song_file
		for song_file in FWN:
			audio = TinyTag.get(f"songs/FWN/{song_file}")
			songs['FWN'][audio.title] = song_file
		for song_file in PS:
			audio = TinyTag.get(f"songs/PS/{song_file}")
			songs['PS'][audio.title] = song_file

		song_lists = {"MemoryBank": MemoryBank_list, "AM": AM_list, "Zero": Zero_list, "FWN": FWN_list, "PS": PS_list,}
		album_durations={}
		for k,v in songs.items():
			d = 0
			for name, file in v.items():
				audio_info = TinyTag.get(f"songs/{k}/{file}")
				d+=audio_info.duration
			album_durations[k]=round(d)
		msg = await voice_channel.send(embeds=[discord.Embed(title='load...'),discord.Embed(title='load...')])
		album_list = []
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
						embed_info.add_field(name="💿 Альбом: ", value=album_name)
						embed_info.add_field(name="⏲️ Тривалість: ",
											 value=f"{math.floor(audio_info.duration / 60)}m {math.floor(audio_info.duration) % 60}s")

						embed2 = discord.Embed()
						if i<len(album_list):
							next_album=album_list[i]
						else:
							next_album=album_list[0]
						embed2.add_field(name=f'Наступний альбом "{albums_names[next_album]}" заграє:', value=f"<t:{round((album_start_time+ datetime.timedelta(seconds=album_durations[album_name])).timestamp())}:R>")
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
								if member.can_send():
									await member.send(f"Адміністрація серверу Dev is Art додала вам 1 нових ачівок:\n- **`{achievements['sde']['name']}`**\n> {achievements['sde']['description']}")



def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(RadioUa(bot))  # add the cog to the bot