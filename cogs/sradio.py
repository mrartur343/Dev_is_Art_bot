import asyncio
import datetime
import json
import math
import random
import time
from os import listdir
from os.path import isfile, join
from modules.radio_ua_views import *

from PIL import Image, ImageDraw
from tinytag import TinyTag
import discord
import sradio_contoller
from discord.ext import commands, pages
import avarage_color_getter
from modules import radio_timetable

with open("other/radio_sleep_timers.json", 'r') as file:
	radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())


class RadioRemove(discord.ui.View):
	def __init__(self, general_radio_ingo_channel, msg_id, bot, *args, **kwargs):
		self.general_radio_ingo_channel: discord.Thread = general_radio_ingo_channel
		self.msg_id: int = msg_id
		self.bot: discord.Bot = bot
		super().__init__(timeout=None, *args)

	@discord.ui.button(label="Видалити плейлист", style=discord.ButtonStyle.gray,
	                   emoji="🗑️")
	async def button_callback1(self, button: discord.ui.Button, interaction: discord.Interaction):

		radio_name = interaction.message.embeds[0].footer.text
		await interaction.message.delete()

		guild = interaction.guild

		with open(f'server_radios/{guild.id}.json', 'r') as file:
			server_radios = json.loads(file.read())

		result = []
		for p in server_radios:
			if p['name'] != radio_name:
				result.append(p)

		with open(f'server_radios/{guild.id}.json', 'w') as file:
			json.dump(result, file)


class RadioPlaylistsView(discord.ui.View):
	def __init__(self, general_radio_ingo_channel, msg_id, bot, cycled, voice_channel, *args, **kwargs):
		self.general_radio_ingo_channel: discord.Thread = general_radio_ingo_channel
		self.msg_id: int = msg_id
		self.bot: discord.Bot = bot
		self.cycled = cycled
		self.voice_channel: discord.VoiceChannel = voice_channel
		super().__init__(timeout=None, *args)

	@discord.ui.button(label="Грати радіо", style=discord.ButtonStyle.gray,
	                   emoji="📻")
	async def button_callback1(self, button: discord.ui.Button, interaction: discord.Interaction):

		radio_name = interaction.message.embeds[0].footer.text
		await interaction.message.delete()

		int_channel: discord.TextChannel = interaction.channel
		await interaction.respond(embed=discord.Embed(title='Радіо вмикається'), ephemeral=True)
		msg = await int_channel.send(embed=discord.Embed(title='load...'))

		cycle = True

		first_play = True

		while cycle:

			all_radios = sradio_contoller.get_server_radio(interaction.guild.id)
			radio_url = ''

			print(all_radios)
			print(radio_name)

			for radio in all_radios:
				if radio['name'] == radio_name:
					radio_url = radio['link']
			print("radio_image...")
			radio_image = await sradio_contoller.playlist_image(radio_url)
			print("radio_image")

			print("songs_names, songs_urls...")
			songs_names, songs_urls = await sradio_contoller.get_songs(radio_url)
			print("songs_names, songs_urls")

			ci = -1
			ctx_voice_channel = self.voice_channel
			vc: discord.VoiceClient = await ctx_voice_channel.connect()
			random_pos = random.randint(0, len(songs_names))

			new_downloads_check = False

			for song_name, song_url in zip(songs_names, songs_urls):

				songs_names_paths, songs_paths = sradio_contoller.get_all_songs_paths()
				if not (song_name in songs_names_paths):
					if not new_downloads_check:
						await interaction.respond("Зачекайте, не всі треки з плейлиста були завантажені...",
						                          ephemeral=True)

					new_downloads_check = True

					sradio_contoller.songs_download(radio_url)
					await asyncio.sleep(3)
					while not (song_name in songs_names_paths):
						songs_names_paths, songs_paths = sradio_contoller.get_all_songs_paths()

			if new_downloads_check:
				await interaction.respond("Плейлист було дозавантажено", ephemeral=True)
			else:
				await interaction.respond("Плейлист повінстю вже був завантажений", ephemeral=True)
			for song_name, song_url in zip(songs_names, songs_urls):
				try:
					if first_play:
						if ci < random_pos:
							ci += 1
							continue

					print(f"Play {song_name} - {song_url}")
					ci += 1

					songs_names_paths, songs_paths = sradio_contoller.get_all_songs_paths()
					if not (song_name in songs_names_paths):
						print(songs_paths)

						sradio_contoller.songs_download(radio_url)
						await asyncio.sleep(3)
						while not (song_name in songs_names_paths):
							songs_names_paths, songs_paths = sradio_contoller.get_all_songs_paths()

					album_durations = {}
					for d_song_path in songs_paths:
						audio_info = TinyTag.get(d_song_path)
						if audio_info.duration != None:
							album_durations[d_song_path] = round(audio_info.duration)

					cycle_duration = 0.0

					for d_song_path in songs_paths:
						cycle_duration += album_durations[d_song_path]

					next_cycle_time = datetime.datetime.now() + datetime.timedelta(seconds=cycle_duration)

					album_start_time = datetime.datetime.now()

					song_path = ""

					i = -1

					for song_name_path in songs_names_paths:
						i += 1
						if song_name == song_name_path:
							song_path = songs_paths[i]

					audio_info = TinyTag.get(song_path, image=True)

					admin_logs = (
						await (await self.bot.fetch_guild(1208129686031310848)).fetch_channel(1208129687067303940))

					dcolor = avarage_color_getter.get_avarage_color_path(audio_info.album)

					w, h = 8192, 64
					shape = [(0, 0), (w, h)]

					# creating new Image object
					img = Image.new("RGB", (w, h))

					# create  rectangleimage
					img1 = ImageDraw.Draw(img)
					img1.rectangle(shape, fill='#%02x%02x%02x' % (dcolor[0], dcolor[1], dcolor[2]))

					img.save('b_line.png')

					file = discord.File("b_line.png", filename="b_line.png")
					line_img_url = "attachment://b_line.png"

					timetable = radio_timetable.get_album_times2(songs_names,
					                                             album_durations, ci,
					                                             album_start_time + datetime.timedelta(
						                                             seconds=album_durations[song_path]),
					                                             songs_names_paths, songs_paths)

					embed_info = discord.Embed(title=audio_info.title,
					                           color=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1],
					                                                        b=dcolor[2]))
					embed_info.set_author(name=radio_name, icon_url=radio_image, url=radio_url)
					track_image = await (sradio_contoller.track_image(song_url))
					if track_image is None:
						track_image = radio_image
					if not (track_image is None):
						embed_info.set_thumbnail(url=track_image)

					embed_info.url = song_url

					embed_info.description = f"{audio_info.artist}  •  {audio_info.album}"

					embed_info.set_image(url=line_img_url)
					embed2 = discord.Embed(title='Розпорядок наступних треків',
					                       color=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1], b=dcolor[2]))
					embed2.description = ''
					embed2.description += ('**Наступні треки:**\n')

					embed2.set_image(url=line_img_url)
					radio_msg_view = AlbumSongs(current_play=song_name, timeout=None, timetable=timetable,
					                            next_cycle_time=next_cycle_time,
					                            cycle_duration=cycle_duration, current_album=song_path,
					                            radio_url=radio_url, audio_info=audio_info)

					i = 0
					single_check = True
					old_emoji = ""
					for k, v in timetable:
						if i < 4 and ci + i + 1 < len(songs_names):
							audio_info = TinyTag.get(k, image=True)
							v: datetime.datetime

							kyiv_h = v.hour

							time_emoji = "🏙️" if 12 <= kyiv_h < 18 else (
								"🌇" if 18 <= kyiv_h < 24 else ('🌇' if 6 <= kyiv_h < 12 else "🌃"))
							if time_emoji != old_emoji:
								embed2.description += f"\n- {time_emoji}\n"

							embed2.description += (
								f"<t:{round(v.timestamp())}:t> {songs_names[ci + i + 1]} {f' (<t:{round(v.timestamp())}:R>)' if (i == 0) else ''}\n")

						old_emoji = time_emoji
						i += 1
					if i < 4:
						embed2.description += (
							f"<t:{round(next_cycle_time.timestamp())}:t> Наступний цикл (довантаження нових альбомів/синглів/плейлистів) {f' (<t:{round(next_cycle_time.timestamp())}:R>)' if (i == 0) and single_check else ''}\n")

					print(embed2.description)

					radio_msg_embeds = [embed_info, embed2]

					waiting_start_time = time.time()
					wait_duration = audio_info.duration

					updated_channel: discord.VoiceChannel = await (vc.channel.guild.fetch_channel(
						vc.channel.id))

					msg = await msg.edit(file=file,embeds=radio_msg_embeds, view=radio_msg_view)

					while len(updated_channel.members) < 2 and time.time() - waiting_start_time < wait_duration:
						updated_channel: discord.VoiceChannel = await (vc.channel.guild.fetch_channel(
							vc.channel.id))
						await asyncio.sleep(1)
					FFMPEG_OPTIONS = {
						'options': f'-vn -b:a 320k -ss {round(time.time() - waiting_start_time)}'}
					audio_source = discord.FFmpegPCMAudio(song_path,
					                                      **FFMPEG_OPTIONS)

					if not (self.bot.user.id in [m.id for m in updated_channel.members]):
						vc = await ctx_voice_channel.connect()

					await vc.play(audio_source, wait_finish=True)

					with open("other/radio_sleep_timers.json", 'r') as file:
						radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())

					if len(updated_channel.members) >= 2:
						voice_channel: discord.VoiceChannel = self.voice_channel
						for member_id in radio_sleep_timers['song_end']:
							user = await voice_channel.guild.fetch_member(member_id)
							if user != None:
								if user.voice != None:
									if user.voice.channel.id == voice_channel.id:
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
												if user.voice.channel.id == voice_channel.id:
													await user.move_to(None)
													radio_sleep_timers[timer_str].remove(m_id)
											try:
												await user.send(f"Надобраніч!")
											except:
												pass

					if first_play:
						first_play = False
				except Exception as e:
					print(e.__str__() + " " + datetime.datetime.now().strftime("%c"))

			if not self.cycled:
				cycle = False


class SRadio(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@discord.slash_command()
	@commands.has_permissions(administrator=True)
	async def add(self, ctx: discord.ApplicationContext,
	              playlist_link: discord.Option(str, description='Посилання на плейлист')):
		guild = ctx.guild
		with open(f'server_radios/{guild.id}.json', 'r') as file:
			server_radios = json.loads(file.read())

		radio_name = sradio_contoller.playlist_name(playlist_link)

		server_radios.append({'name': radio_name, 'link': playlist_link})

		with open(f'server_radios/{guild.id}.json', 'w') as file:
			json.dump(server_radios, file)

	@discord.slash_command()
	@commands.has_permissions(administrator=True)
	async def remove(self, ctx: discord.ApplicationContext,
	                 playlist_link: discord.Option(str, description='Посилання на плейлист')):

		server_radios = sradio_contoller.get_server_radio(ctx.guild.id)

		embeds = []

		for radio in server_radios:
			embed = discord.Embed(title=radio['name'])
			embed.url = radio['link']
			playlist_image = await sradio_contoller.playlist_image(radio['link'])
			if not (playlist_image is None):
				embed.set_image(url=playlist_image)
			embed.set_footer(text=radio['name'])

			embeds.append(embed)

		paginator = pages.Paginator(
			embeds,
			timeout=None
		)

		pmsg = await paginator.respond(ctx.interaction)
		custom_v = RadioRemove(pmsg.channel, pmsg.id, self.bot)

		await paginator.update(pages=embeds, custom_view=custom_v)

	@discord.slash_command()
	@commands.has_permissions(administrator=True)
	async def play(self, ctx: discord.ApplicationContext, voice_channel: discord.Option(discord.VoiceChannel),
	               cycled: discord.Option(bool, required=False) = True):

		server_radios = sradio_contoller.get_server_radio(ctx.guild.id)

		embeds = []

		for radio in server_radios:
			embed = discord.Embed(title=radio['name'])
			embed.url = radio['link']
			playlist_image = await sradio_contoller.playlist_image(radio['link'])
			if not (playlist_image is None):
				embed.set_image(url=playlist_image)
			embed.set_footer(text=radio['name'])

			embeds.append(embed)

		paginator = pages.Paginator(
			embeds,
			timeout=None
		)

		pmsg = await paginator.respond(ctx.interaction)
		custom_v = RadioPlaylistsView(pmsg.channel, pmsg.id, self.bot, cycled, voice_channel)

		await paginator.update(pages=embeds, custom_view=custom_v)
	@discord.slash_command()
	@commands.has_permissions()
	async def info(self, ctx: discord.ApplicationContext):

		embed_info = discord.Embed(title="SRadio Bot")

		embed_info.description = documentation_text

		await ctx.respond(embed=embed_info, view=documentation_view)

	@discord.slash_command()  # we can also add application commands
	async def list(self, ctx: discord.ApplicationContext):
		server_radios = sradio_contoller.get_server_radio(ctx.guild.id)

		embeds = []

		for radio in server_radios:
			embed = discord.Embed(title=radio['name'])
			embed.url = radio['link']
			playlist_image = await sradio_contoller.playlist_image(radio['link'])
			if not (playlist_image is None):
				embed.set_image(url=playlist_image)
			embeds.append(embed)

		paginator = pages.Paginator(
			embeds,
			timeout=None
		)

		await paginator.respond(ctx.interaction)


	@commands.Cog.listener()  # we can add event listeners to our cog
	async def on_guild_join(self, guild: discord.Guild):  # this is called when a member joins the server
		# you must enable the proper intents
		# to access this event.
		# See the Popular-Topics/Intents page for more info
		with open(f'server_radios/{guild.id}.json', 'w') as file:
			json.dump([
				{
					"name": "Плейлист невідомого поета",
					"link": "https://open.spotify.com/playlist/5SMhA3BNpFA7mJNk5LFHxV?si=1ee1481307f34f7b"
				}], file)


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(SRadio(bot))  # add the cog to the bot
