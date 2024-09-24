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
import jmespath
from discord.ext import commands, pages

import avarage_color_getter
from modules import sradio_contoller, radio_timetable


async def get_radios(ctx: discord.AutocompleteContext):
	all_radios = sradio_contoller.get_server_radio(ctx.interaction.guild.id)
	return jmespath.search('[*].name', all_radios)


class SRadio(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot = bot

	@discord.slash_command()  # we can also add application commands
	async def play_radio(self, ctx: discord.ApplicationContext,
	                     radio_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_radios)),
	                     cycled: discord.Option(bool, required=False) = True
	                     ):


		msg = ctx.respond(embed=discord.Embed(title='load...'))
		all_radios = sradio_contoller.get_server_radio(ctx.interaction.guild.id)
		radio_url = ''

		for radio in all_radios:
			if radio['name'] == radio_name:
				radio_url=radio['link']

		radio_queue = sradio_contoller.get_songs(radio_url)

		cycle = True


		ctx_voice_channel = ctx.author.voice.channel

		if ctx_voice_channel is None:
			return

		async for message in ctx.channel.history():
			if message.author.id == self.bot.user.id:
				await message.delete()



		while cycle:
			ci = -1
			for song_name, song_url in radio_queue:
				ci+=1


				actual_songs_paths = sradio_contoller.get_all_songs_paths()

				while not (song_name in jmespath.search('[*][0]', actual_songs_paths)):
					await ctx.channel.send('Зачекайте, не всі треки з плейлиста були завантажені...')
					sradio_contoller.songs_download(radio_url)
					await asyncio.sleep(3)
					actual_songs_paths = sradio_contoller.get_all_songs_paths()
				await ctx.channel.send('Плейлист було дозавантажено!')

				album_durations = {}
				for d_song_path in jmespath.search('[*][1]', actual_songs_paths):
					audio_info = TinyTag.get(d_song_path)
					if audio_info.duration != None:
						album_durations[d_song_path] = round(audio_info.duration)

				cycle_duration=0.0

				for d_song_path in jmespath.search('[*][1]', actual_songs_paths):
					cycle_duration += album_durations[d_song_path]

				next_cycle_time = datetime.datetime.now() + datetime.timedelta(seconds=cycle_duration)

				album_start_time = datetime.datetime.now()

				song_path = jmespath.search(f'[?[0]== {song_name}][1]', actual_songs_paths)

				audio_info = TinyTag.get(song_path)

				image_data: bytes = audio_info.get_image()
				with open('a.png', 'wb') as file:
					file.write(image_data)
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


				file = discord.File(fp='a.png')
				imgmsg:discord.Message = await admin_logs.send(content=".", file=file)

				timetable = radio_timetable.get_album_times2(jmespath.search('[*][0]', actual_songs_paths),
				                                            album_durations, ci,
				                                            album_start_time + datetime.timedelta(
					                                            seconds=album_durations[song_path]))



				embed_info = discord.Embed(title='Зараз грає:',
				                           color=discord.Color.from_rgb(r=dcolor[0], g=dcolor[1],
				                                                        b=dcolor[2]))
				embed_info.set_thumbnail(url=imgmsg.attachments[0].url)

				embed_info.add_field(name="🎵 Назва:", value=audio_info.title)
				embed_info.add_field(name="🧑‍🎤 Виконавець: ", value=audio_info.artist)
				embed_info.add_field(name="⌛ Рік випуску: ",
				                     value=audio_info.year if str(audio_info.year) != '1970' else '???')
				embed_info.add_field(name="💿 Альбом: ",
				                     value=audio_info.album)

				embed_info.add_field(name="⏲️ Тривалість: ",
				                     value=f"{math.floor(audio_info.duration / 60)}m {math.floor(audio_info.duration) % 60}s")
				embed_info.add_field(name="📻 Наступний трек: ",
				                     value=f"{radio_queue[ci + 1] if ci + 1 < len(radio_queue) else  '???'}  <t:{round((datetime.datetime.now() + datetime.timedelta(seconds=audio_info.duration)).timestamp())}:R>")
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

						embed2.description += (
								f"<t:{round(v.timestamp())}:t> {audio_info.title} {f' (<t:{round(v.timestamp())}:R>)' if (i == 0) else ''}\n")

					old_emoji = time_emoji
				if i < 6:
					embed2.description += (
						f"<t:{round(next_cycle_time.timestamp())}:t> Наступний цикл (довантаження нових альбомів/синглів/плейлистів) {f' (<t:{round(next_cycle_time.timestamp())}:R>)' if (i == 0) and single_check else ''}\n")
				embed2.set_footer(text='Між кожним альбомом грають 2 випадкових синглів')

				radio_msg_embeds = [embed_info, embed2]
				radio_msg_view = AlbumSongs( current_play=song_name, timeout=None, timetable=timetable,
				                            next_cycle_time=next_cycle_time,
				                            cycle_duration=cycle_duration,current_album=song_path)

				sde_achievement_list = []

				vc: discord.VoiceClient = await ctx_voice_channel.connect()

				waiting_start_time = time.time()
				wait_duration = audio_info.duration

				updated_channel: discord.VoiceChannel = asyncio.run(vc.channel.guild.fetch_channel(
					vc.channel.id))

				msg = await msg.edit(embeds=radio_msg_embeds, view=radio_msg_view)


				while len(updated_channel.members)<2 and time.time() - waiting_start_time < wait_duration:
					updated_channel: discord.VoiceChannel = asyncio.run(vc.channel.guild.fetch_channel(
						vc.channel.id))
					await asyncio.sleep(1)
				FFMPEG_OPTIONS = {
					'options': f'-vn -b:a 320k -ss {round(time.time() - waiting_start_time)}'}
				audio_source = discord.FFmpegPCMAudio(song_path,
				                                      **FFMPEG_OPTIONS)


				await vc.play(audio_source,wait_finish=True)






			if not cycled:
				cycle = False

	@discord.slash_command()  # we can also add application commands
	async def list(self, ctx: discord.ApplicationContext):
		server_radios = sradio_contoller.get_server_radio(ctx.guild.id)

		embeds = []

		for radio in server_radios:
			embed = discord.Embed(title=radio['name'])
			embed.add_field(name='Радіо плейлист:', value=radio['link'])
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
