import asyncio
import json
import math
import datetime
import os
import random
import time
from PIL import Image, ImageDraw
from discord import Thread
import threading
import avarage_color_getter
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
from modules.radio_ua_views import *


another_radio_info_messages: typing.Dict[int, discord.Message] = {}

async def guild_play(play_source_path:discord.AudioSource,audio_info:TinyTag,radio_voice_client: discord.VoiceClient | discord.VoiceProtocol):
	updated_channel: discord.VoiceChannel = await radio_voice_client.channel.guild.fetch_channel(
		radio_voice_client.channel.id)

	if len(updated_channel.members) < 2:
		quality_high = False
	else:
		quality_high = True

	waiting_start_time = time.time()
	wait_duration = audio_info.duration
	while not quality_high and time.time() - waiting_start_time < wait_duration:
		await asyncio.sleep(1)
		updated_channel: discord.VoiceChannel = await radio_voice_client.channel.guild.fetch_channel(
			radio_voice_client.channel.id)



		if len(updated_channel.members) >= 2:
			quality_high = True
	FFMPEG_OPTIONS = {
		'options': f'-vn -b:a 320k -ss {round(time.time() - waiting_start_time)}'}
	audio_source = discord.FFmpegPCMAudio(play_source_path,
	                                      **FFMPEG_OPTIONS)
	if time.time() - waiting_start_time < wait_duration:
		await radio_voice_client.play(audio_source, wait_finish=True)

async def radio_all_play(play_source_path: str, bot: discord.Bot, radio_info_embeds: typing.List[discord.Embed],radio_info_view: discord.ui.View,audio_info):
	global another_radio_info_messages

	with open("other/another_guilds_radio.json", 'r') as file:
		another_guilds_radio: typing.Dict[str , typing.Tuple[typing.List[int], int]] = json.loads(file.read())

	async for guild in bot.fetch_guilds():
		print(f"Play guild: {guild.name}")
		another_radio_ids = another_guilds_radio[str(guild.id)]

		radio_play_channel: discord.VoiceChannel = await guild.fetch_channel(another_radio_ids[1])

		if guild.id in another_radio_info_messages:
			await another_radio_info_messages[guild.id].edit(embeds=radio_info_embeds)
		else:
			if len(another_radio_ids[0])==1:
				info_channel = await guild.fetch_channel(another_radio_ids[0][0])
			else:
				forum_channel =  await guild.fetch_channel(another_radio_ids[0][0])
				info_channel = forum_channel.get_thread(another_radio_ids[0][1])

			async for message in info_channel.history():
				if message.author.id == bot.user.id:
					await message.delete()

			msg= await info_channel.send(embeds=radio_info_embeds)
			another_radio_info_messages[guild.id]=msg

		if guild.voice_client:
			voice = guild.voice_client
		else:
			voice = await radio_play_channel.connect()



		asyncio.run(guild_play(play_source_path,audio_info, voice))



with open("other/songs_lists_cache.json", 'r') as file:
	songs_lists_cache = json.loads(file.read())
with open("other/albums_images_cache.json", 'r') as file:
	albums_images_cache = json.loads(file.read())
with open("other/radio_sleep_timers.json", 'r') as file:
	radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())


def get_song_list(url: str):
	global songs_lists_cache

	if url in songs_lists_cache:
		return songs_lists_cache[url]
	else:
		r_onlineradio = requests.get(url).content

		soup = BeautifulSoup(r_onlineradio, 'html.parser')

		song_names = [heading.text for heading in
		              soup.find_all('span', class_='ListRowTitle__LineClamp-sc-1xe2if1-0 jjpOuK')]
		songs_lists_cache[url] = song_names
		with open('other/songs_lists_cache.json', 'w') as file:
			json.dump(songs_lists_cache, file)
		return song_names


def get_album_name_and_key(url: str):
	r_onlineradio = requests.get(url).content

	soup = BeautifulSoup(r_onlineradio, 'html.parser')

	album_name = [heading.text for heading in
	              soup.find_all('h1', class_='Type__TypeElement-sc-goli3j-0 ofaEA gj6rSoF7K4FohS2DJDEm')][0]
	album_key = url[31:]
	return (album_name, album_key)


class RadioUa(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot, radio_name: str):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot
		self.radio_name = radio_name


	@commands.Cog.listener()
	async def on_ready(self):
		print("Radio: ON")

		albums_imgs = albums_images_cache
		start_check = True


		with open('other/radio_playlists.json', 'r') as file:
			radio_playlist = json.loads(file.read())[self.radio_name]



		while True:

			album_short_names_nf = [f for f in listdir('songs')]
			album_short_names = []
			for asn_nf in album_short_names_nf:
				if asn_nf in radio_playlist:
					album_short_names.append(asn_nf)

			songs = {}
			with open('other/albums_data.json', 'r') as file:
				album_data_json_nf = json.loads(file.read())
				album_data_json = {}
				for ak, ad in album_data_json_nf.items():
					if ak in radio_playlist:
						album_data_json[ak] = ad
			singles_names = []
			with open('other/singles_names.json', 'r') as file:
				singles_names_nf = json.loads(file.read())
				singles_names = []
				for s_name in singles_names_nf:
					if s_name in radio_playlist:
						singles_names.append(s_name)
			albums_names = {}
			albums_url = {}
			for short_name, info in album_data_json.items():
				albums_names[short_name] = info[0]
				albums_url[short_name] = info[1]
			song_files = {}

			for short_name in album_short_names:
				song_files[short_name] = [f for f in listdir(f"songs/{short_name}") if
				                          isfile(join(f"songs/{short_name}", f))]

			# noinspection PyTypeChecker



			admin_logs = (await (await self.bot.fetch_guild(1208129686031310848)).fetch_channel(1208129687067303940))
			# noinspection PyTypeChecker
			afk_radio: discord.VoiceChannel = await self.bot.fetch_channel(1235991951547961478)
			await admin_logs.send(f'Cycle {datetime.datetime.now().strftime(format="%c")}')
			if start_check:
				await admin_logs.send(f"## (start {self.radio_name})")
				start_check = False

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
					if audio_info.duration != None:
						d += audio_info.duration
				album_durations[k] = round(d)

			all_radio_time = 0.0

			for duration in album_durations.values():
				all_radio_time += duration
			if self.radio_name == 'Alpha':
				general_radio_info = (await (await self.bot.fetch_guild(1208129686031310848)).fetch_channel(1241408420284989494)).get_thread(1241410417985720411)

				async for message in general_radio_info.history():
					if message.author.id == self.bot.user.id:
						await message.delete()
				await general_radio_info.send("Додаткова інформація:",
				                              view=GeneralRadioInfo(all_radio_time=all_radio_time))

			song_lists = []
			random.shuffle(singles_names)
			random.shuffle(album_short_names)
			for single_name in singles_names:
				if single_name in album_short_names:
					album_short_names.remove(single_name)
			i = 0
			album_list = []
			st = datetime.datetime.now()

			j = 0

			cycle_duration = 0.0

			album_likes = {}
			with open("other/album_likes.json", 'r') as file:
				album_likes = json.loads(file.read())
			for album in album_list:
				if album in album_likes:
					continue
				album_likes[album] = []
			with open("other/album_likes.json", 'w') as file:
				json.dump(album_likes, file)

			####

			i = 0
			song_lists = []

			#######

			radio_album_list = []
			i = 0

			random.shuffle(album_short_names)
			random.shuffle(singles_names)

			st = datetime.datetime.now()
			for short_name in album_short_names:

				st += datetime.timedelta(seconds=album_durations[short_name])
				radio_album_list.append(short_name)
				for _ in range(2):
					if i >= len(singles_names):
						i = 0
					st += datetime.timedelta(seconds=album_durations[singles_names[i]])
					radio_album_list.append(singles_names[i])
					i += 1

			#####

			album_list = radio_album_list
			for album_name in radio_album_list:
				song_lists.append([album_name, get_song_list(albums_url[album_name])])

			def members_ids(members):
				r = [m.id for m in members]
				if self.bot.user.id in r:
					r.remove(self.bot.user.id)
				return r


			for album_name, _ in song_lists:
				cycle_duration += album_durations[album_name]

			next_cycle_time = datetime.datetime.now() + datetime.timedelta(seconds=cycle_duration)
			await admin_logs.send(
				f'Cycle duration: {math.floor((cycle_duration / 60) / 60)} h {math.floor((cycle_duration % 3600) / 60)} m {math.floor(cycle_duration % 60)} s (next cycle: <t:{round(next_cycle_time.timestamp())}:F>)')
			album_count = -1

			for album_name, songs_list in song_lists:
				album_count += 1
				i += 1
				album_start_time = datetime.datetime.now()
				next_index = album_count + 3
				timetable = radio_timetable.get_album_times(jmespath.search("[*][0]", song_lists),
				                                            album_durations, album_count,
				                                            album_start_time + datetime.timedelta(
					                                            seconds=album_durations[album_name]))

				async def send_album_not(next_album_index: int):
					with open("other/album_likes.json", 'r') as file:
						album_likes = json.loads(file.read())
						for user_like in album_likes[album_list[next_album_index]]:
							user = await self.bot.fetch_user(user_like)
							not_check = True
							with open('other/notifications_off.json', 'r') as file:
								notifications_off: typing.Dict[str, typing.List[str]] = json.loads(file.read())
								if str(user_like) in notifications_off.keys():
									if album_list[next_album_index] in notifications_off[str(user_like)]:
										not_check = False
							if user.can_send() and not_check and ((next_album_index - album_count) - 1) < len(
									timetable):
								next_album_timestamp = timetable[(next_album_index - album_count) - 1][1].timestamp()
								album_notification_label = "Сингл" if album_list[
									                                      next_album_index] in singles_names else "Альбом"
								await user.send(
									f"{album_notification_label} **`{albums_names[album_list[next_album_index]]}`**, який ви вподобали, буде грати на радіо <t:{round(next_album_timestamp)}:R>",
									view=DislikeAlbum(timeout=None, liked_album=album_list[next_album_index]))

				if next_index >= len(album_list):
					pass
				elif next_index == 0:
					for next_index2 in range(3):
						await send_album_not(next_index2)
				else:
					await send_album_not(next_index)

				dcolor = avarage_color_getter.get_avarage_color(album_name)

				w, h = 8192, 64
				shape = [(0, 0), (w, h)]

				# creating new Image object
				img = Image.new("RGB", (w, h))

				# create  rectangleimage
				img1 = ImageDraw.Draw(img)
				img1.rectangle(shape, fill='#%02x%02x%02x' % (dcolor[0], dcolor[1], dcolor[2]))

				img.save('b_line.png')

				file = discord.File(fp='b_line.png')
				imgmsg = await admin_logs.send(content=".", file=file)
				line_img_url = imgmsg.attachments[0].url

				for song_name in songs_list:
					if song_name in songs[album_name]:
						try:
							await admin_logs.send(
								f'Play {song_name} ({album_name}) ({datetime.datetime.now().strftime(format="%c")})')
							file_name = songs[album_name][song_name]

							quality = 320



							audio_info = TinyTag.get(f"songs/{album_name}/{file_name}", image=True)
							if not album_name in albums_imgs:
								image_data: bytes = audio_info.get_image()
								with open('a.png', 'wb') as file:
									file.write(image_data)

								file = discord.File(fp='a.png')
								imgmsg = await admin_logs.send(content=".", file=file)
								albums_imgs[album_name] = imgmsg.attachments[0].url
								with open('other/albums_images_cache.json', 'w') as file:
									json.dump(albums_imgs, file)

							embed_info = discord.Embed(title='Зараз грає:',
							                           color=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1],
							                                                        b=dcolor[2]))
							embed_info.set_thumbnail(url=albums_imgs[album_name])

							embed_info.add_field(name="🎵 Назва:", value=audio_info.title)
							embed_info.add_field(name="🧑‍🎤 Виконавець: ", value=audio_info.artist)
							embed_info.add_field(name="⌛ Рік випуску: ",
							                     value=audio_info.year if str(audio_info.year) != '1970' else '???')
							embed_info.add_field(name="💿 Альбом: " if (not album_name in singles_names) else "Сингл ⚡:",
							                     value=albums_names[album_name] if (
								                     not album_name in singles_names) else "Між кожним альбомом грають 2 випадкових сингла")

							embed_info.add_field(name="⏲️ Тривалість: ",
							                     value=f"{math.floor(audio_info.duration / 60)}m {math.floor(audio_info.duration) % 60}s")
							embed_info.add_field(name="📻 Наступний трек: ",
							                     value=f"{songs_list[songs_list.index(song_name) + 1] if songs_list.index(song_name) + 1 < len(songs_list) else (f'{song_lists[album_count + 1][1][0]} з {albums_names[song_lists[album_count + 1][0]]}' if album_count + 1 < len(song_lists) else '???')}  <t:{round((datetime.datetime.now() + datetime.timedelta(seconds=audio_info.duration)).timestamp())}:R>")
							embed_info.set_image(url=line_img_url)
							embed2 = discord.Embed(title='Розпорядок наступних альбомів',
							                       color=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1], b=dcolor[2]))
							embed2.description = ''
							embed2.set_image(url=line_img_url)

							i = 0
							single_check = True
							old_emoji = ""
							for k, v in timetable:
								if i < 6:
									v: datetime.datetime

									kyiv_h = v.hour

									time_emoji = "🏙️" if 12 <= kyiv_h < 18 else (
										"🌇" if 18 <= kyiv_h < 24 else ('🌇' if 6 <= kyiv_h < 12 else "🌃"))
									if time_emoji != old_emoji:
										embed2.description += f"\n- {time_emoji}\n"
									if i == 0 and (k in singles_names) and single_check:
										single_check = False
										embed2.description += f"⚡ <t:{round(v.timestamp())}:t> Випадковий сингл (<t:{round(v.timestamp())}:R>)\n"
										embed2.description += "-----\n"
									elif (not k in singles_names) and k != album_name:
										embed2.description += (
											f"<t:{round(v.timestamp())}:t> {albums_names[k]} {f' (<t:{round(v.timestamp())}:R>)' if (i == 0) and single_check else ''}\n")
										i += 1

								old_emoji = time_emoji
							if i < 6:
								embed2.description += (
									f"<t:{round(next_cycle_time.timestamp())}:t> Наступний цикл (довантаження нових альбомів/синглів/плейлистів) {f' (<t:{round(next_cycle_time.timestamp())}:R>)' if (i == 0) and single_check else ''}\n")
							embed2.set_footer(text='Між кожним альбомом грають 2 випадкових синглів')
							if len(jmespath.search("[*][0]", song_lists)) == 1:
								embed2 = discord.Embed(description='Цей сингл є початком циклу музики на радіо',
								                       colour=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1],
								                                                     b=dcolor[2]))

							radio_msg_embeds = [embed_info, embed2]
							radio_msg_view = AlbumSongs(songs_list=songs_list, current_play=song_name, timeout=None,
							                               current_album=album_name, timetable=timetable,
							                               next_cycle_time=next_cycle_time,
							                               cycle_duration=cycle_duration)

							sde_achievement_list = []


							await self.bot.change_presence(status=discord.Status.streaming,
							                               activity=discord.Activity(
								                               type=discord.ActivityType.listening,
								                               name=f"{audio_info.title} - {audio_info.artist} | ({albums_names[album_name]})"))



							await radio_all_play(f"songs/{album_name}/{file_name}",self.bot,radio_msg_embeds,radio_msg_view,audio_info)


							with open("other/radio_sleep_timers.json", 'r') as file:
								radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())


							for guild in self.bot.guilds:
								if guild.voice_client:
									voice_channel: discord.VoiceChannel = guild.voice_client.channel
									for member_id in radio_sleep_timers['song_end']:
										user = await voice_channel.guild.fetch_member(member_id)
										if user != None:
											if user.voice != None:
												if user.voice.channel.id == self.radio_channel_id:
													await user.move_to(None)
													radio_sleep_timers['song_end'].remove(member_id)
											try:
												await user.send(f"Надобраніч!")
											except:
												pass

									for timer_str, st_members_ids in radio_sleep_timers.items():
										if timer_str.endswith('m'):
											r_timestamp = int(timer_str.split('m')[0])
											if r_timestamp < datetime.datetime.now().timestamp():
												for m_id in st_members_ids:
													user = await voice_channel.guild.fetch_member(m_id)
													if user != None:
														if user.voice != None:
															if user.voice.channel.id == self.radio_channel_id:
																await user.move_to(None)
																radio_sleep_timers[timer_str].remove(m_id)
														try:
															await user.send(f"Надобраніч!")
														except:
															pass

						except Exception as error:
							await admin_logs.send(
								f"Помилка при завантажені трека: {song_name} ({albums_names[album_name]})\n{error.__str__()}")
							continue


				with open("other/radio_sleep_timers.json", 'r') as file:
					radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())

				for guild in self.bot.guilds:
					if guild.voice_client:
						voice_channel: discord.VoiceChannel  = guild.voice_client.channel

						for member_id in radio_sleep_timers['album_end']:
							user = await voice_channel.guild.fetch_member(member_id)
							if user != None:
								if user.voice != None:
									if user.voice.channel.id == self.radio_channel_id:
										await user.move_to(None)
										radio_sleep_timers['album_end'].remove(member_id)
								try:
									await user.send(f"Надобраніч!")
								except:
									pass


async def setup(bot):  # this is called by Pycord to setup the cog
	pass  # add the cog to the bot
