import discord
from discord.ext import commands
import requests
import time

class RadioUa(commands.Cog): # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot): # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot
		print("Radio: ON")

	def load_audio(self):
		stream_url = 'https://online.hitfm.ua/HitFM_Top'

		r = requests.get(stream_url, stream=True)

		with open(f'stream/stream_{self.i}.mp3', 'wb') as f:
			f.write(b"")
			start_time = time.time()
			try:
				for block in r.iter_content(1024):
					f.write(block)
			except KeyboardInterrupt:
				pass
	@commands.slash_command(name="radio_stop", description="🛸 | Зупинити радіо") # we can add event listeners to our cog
	async def radio_stop(self,ctx: discord.ApplicationContext):

		voice_channel: discord.VoiceChannel = ctx.author.voice.channel
		if voice_channel==None:
			await ctx.respond("Зайдіть у голосовий канал!")
			return
		await ctx.respond("Радіо вимкнено 🛸")
		await ctx.voice_client.disconnect()
	@commands.slash_command(name="radio", description="🛸 | Запустити радіо") # we can add event listeners to our cog
	async def radio(self,ctx: discord.ApplicationContext, radio_station=discord.Option(str, choices=['HitFM', 'RadioRoks', "Класичне радіо"])):
		stream_url = 'https://online.hitfm.ua/HitFM_Top'
		match radio_station:
			case "HitFM":
				stream_url = 'https://online.hitfm.ua/HitFM_Top'
			case "RadioRoks":
				stream_url = 'https://online.radioroks.ua/RadioROKS'
			case "Класичне радіо":
				stream_url = 'https://online.classicradio.com.ua/ClassicRadio'

		r = requests.get(stream_url, stream=True)
		voice_channel: discord.VoiceChannel = ctx.author.voice.channel
		if voice_channel==None:
			await ctx.respond("Зайдіть у голосовий канал!")
			return
		if ctx.voice_client!=None:
			await ctx.respond("Зачекайте зміну радіо...")
			await ctx.voice_client.disconnect()
		voice_client: discord.VoiceClient = await voice_channel.connect()

		try:
			await ctx.respond("Радіо увімкнено 🛸")
			while True:
				for block in r.iter_content(4096*50):


					with open(f'stream/stream.mp3', 'wb') as f:
						f.write(block)

					print("Loaded")
					audio_source = discord.FFmpegPCMAudio(f"stream/stream.mp3")

					start_timer = time.time()
					while voice_client.is_playing():

						if start_timer+0.5<time.time():
							start_timer=time.time()
							print("is playing")
					print("stop")
					print("play...")
					await voice_client.play(audio_source, wait_finish=True)
					if len(voice_channel.members)<1:
						await voice_client.disconnect()
					print("played")
		except KeyboardInterrupt:
			print("пук пук")

def setup(bot): # this is called by Pycord to setup the cog
	bot.add_cog(RadioUa(bot)) # add the cog to the bot