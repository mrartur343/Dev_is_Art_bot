import asyncio
import datetime
import json
import math
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

class RadioPlaylistsView(discord.ui.View):
	def __init__(self,general_radio_ingo_channel,msg_id,bot,cycled,voice_channel, *args, **kwargs):
		self.general_radio_ingo_channel: discord.Thread = general_radio_ingo_channel
		self.msg_id: int = msg_id
		self.bot = bot
		self.cycled = cycled
		self.voice_channel = voice_channel
		super().__init__(timeout=None, *args)

	@discord.ui.button(label="Грати радіо", style=discord.ButtonStyle.gray,
	                   emoji="📻")
	async def button_callback1(self, button:discord.ui.Button, interaction: discord.Interaction):


		radio_name = interaction.message.embeds[0].footer.text

		msg: discord.InteractionMessage = await ((await interaction.respond(embed=discord.Embed(title='load...'))).original_message)



		all_radios = sradio_contoller.get_server_radio(interaction.guild.id)
		radio_url = ''

		print(all_radios)
		print(radio_name)



		for radio in all_radios:
			if radio['name'] == radio_name:
				radio_url = radio['link']

		songs_names, songs_urls = sradio_contoller.get_songs(radio_url)



		cycle = True

		ctx_voice_channel = self.voice_channel
		vc: discord.VoiceClient = await ctx_voice_channel.connect()


		while cycle:
			ci = -1
			for song_name, song_url in zip(songs_names, songs_urls):
				print(f"Play {song_name} - {song_url}")
				ci += 1

				songs_names_paths,songs_paths = sradio_contoller.get_all_songs_paths()
				print("Зачекайте, не всі треки з плейлиста були завантажені...")
				if not (song_name in songs_names_paths):
					print(songs_paths)

					sradio_contoller.songs_download(radio_url)
					await asyncio.sleep(3)
					while not (song_name in songs_names_paths):
						songs_names_paths,songs_paths = sradio_contoller.get_all_songs_paths()
				print("Плейлист було дозавантажено")

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

				i=-1

				for song_name_path in songs_names_paths:
					i+=1
					if song_name==song_name_path:
						song_path=songs_paths[i]

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

				file = discord.File(fp='b_line.png')
				imgmsg = await admin_logs.send(content=".", file=file)
				line_img_url = imgmsg.attachments[0].url


				timetable = radio_timetable.get_album_times2(songs_paths,
				                                             album_durations, ci,
				                                             album_start_time + datetime.timedelta(
					                                             seconds=album_durations[song_path]))

				embed_info = discord.Embed(title='Зараз грає:',
				                           color=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1],
				                                                        b=dcolor[2]))
				embed_info.set_thumbnail(url=sradio_contoller.track_image(song_url))

				embed_info.add_field(name="🎵 Назва:", value=audio_info.title)
				embed_info.add_field(name="🧑‍🎤 Виконавець: ", value=audio_info.artist)
				embed_info.add_field(name="⌛ Рік випуску: ",
				                     value=audio_info.year if str(audio_info.year) != '1970' else '???')
				embed_info.add_field(name="💿 Альбом: ",
				                     value=audio_info.album)

				embed_info.add_field(name="⏲️ Тривалість: ",
				                     value=f"{math.floor(audio_info.duration / 60)}m {math.floor(audio_info.duration) % 60}s")
				embed_info.add_field(name="📻 Наступний трек: ",
				                     value=f"{songs_names[ci + 1] if ci + 1 < len(songs_names) else '???'}  <t:{round((datetime.datetime.now() + datetime.timedelta(seconds=audio_info.duration)).timestamp())}:R>")
				embed_info.set_image(url=line_img_url)
				embed2 = discord.Embed(title='Розпорядок наступних альбомів',
				                       color=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1], b=dcolor[2]))
				embed2.description = ''
				embed2.set_image(url=line_img_url)

				embed2.set_footer(text=f'Грає {radio_name}', icon_url=radio_url)

				i = 0
				single_check = True
				old_emoji = ""
				for k, v in timetable:
					if i < 6:
						audio_info = TinyTag.get(k, image=True)
						v: datetime.datetime

						kyiv_h = v.hour

						time_emoji = "🏙️" if 12 <= kyiv_h < 18 else (
							"🌇" if 18 <= kyiv_h < 24 else ('🌇' if 6 <= kyiv_h < 12 else "🌃"))
						if time_emoji != old_emoji:
							embed2.description += f"\n- {time_emoji}\n"

						embed2.description += (
							f"<t:{round(v.timestamp())}:t> {songs_names[ci+i+1]} {f' (<t:{round(v.timestamp())}:R>)' if (i == 0) else ''}\n")

					old_emoji = time_emoji
					i+=1
				if i < 6:
					embed2.description += (
						f"<t:{round(next_cycle_time.timestamp())}:t> Наступний цикл (довантаження нових альбомів/синглів/плейлистів) {f' (<t:{round(next_cycle_time.timestamp())}:R>)' if (i == 0) and single_check else ''}\n")
				embed2.set_footer(text='Між кожним альбомом грають 2 випадкових синглів')

				print(embed2.description)

				radio_msg_embeds = [embed_info, embed2]
				radio_msg_view = AlbumSongs(current_play=song_name, timeout=None, timetable=timetable,
				                            next_cycle_time=next_cycle_time,
				                            cycle_duration=cycle_duration, current_album=song_path)




				waiting_start_time = time.time()
				wait_duration = audio_info.duration

				updated_channel: discord.VoiceChannel = await (vc.channel.guild.fetch_channel(
					vc.channel.id))

				msg = await msg.edit(embeds=radio_msg_embeds, view=radio_msg_view)

				while len(updated_channel.members) < 2 and time.time() - waiting_start_time < wait_duration:
					updated_channel: discord.VoiceChannel = await (vc.channel.guild.fetch_channel(
						vc.channel.id))
					await asyncio.sleep(1)
				FFMPEG_OPTIONS = {
					'options': f'-vn -b:a 320k -ss {round(time.time() - waiting_start_time)}'}
				audio_source = discord.FFmpegPCMAudio(song_path,
				                                      **FFMPEG_OPTIONS)

				await vc.play(audio_source, wait_finish=True)

				with open("other/radio_sleep_timers.json", 'r') as file:
					radio_sleep_timers: typing.Dict[str, typing.List[int]] = json.loads(file.read())

				if len(updated_channel.members) >=2:
					voice_channel: discord.VoiceChannel  =self.voice_channel
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

			if not self.cycled:
				cycle = False



class SRadio(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot = bot

	@discord.slash_command()
	@commands.has_permissions(administrator=True)
	async def play(self, ctx: discord.ApplicationContext,voice_channel: discord.Option(discord.VoiceChannel), cycled: discord.Option(bool,required=False)=True):

		server_radios = sradio_contoller.get_server_radio(ctx.guild.id)

		embeds = []

		for radio in server_radios:
			embed = discord.Embed(title=radio['name'])
			embed.add_field(name='Радіо плейлист:', value=radio['link'])
			embed.set_footer(text=radio['name'])
			embeds.append(embed)

		paginator = pages.Paginator(
			embeds,
			timeout=899
		)

		pmsg = await paginator.respond(ctx.interaction,ephemeral=True)
		custom_v =RadioPlaylistsView(pmsg.channel,pmsg.id,self.bot,cycled,voice_channel)

		await paginator.update(pages=embeds,custom_view=custom_v)

	@discord.slash_command()  # we can also add application commands
	async def list(self, ctx: discord.ApplicationContext):
		server_radios = sradio_contoller.get_server_radio(ctx.guild.id)

		embeds = []

		for radio in server_radios:
			embed = discord.Embed(title=radio['name'])
			embed.url =radio['link']
			embed.set_image(url = sradio_contoller.playlist_image(radio['link']))
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
					"name": "Background music",
					"link": "https://open.spotify.com/playlist/5SMhA3BNpFA7mJNk5LFHxV?si=1ee1481307f34f7b"
				}], file)


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(SRadio(bot))  # add the cog to the bot
