import discord
from discord.ext import commands
import requests
import time
radio_list = {
			"HitFM": "https://online.hitfm.ua/HitFM_Top",
			"RadioRoks": 'https://online.radioroks.ua/RadioROKS',
			"KissFM": "https://online.kissfm.ua/KissFM"
		}
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

	@commands.slash_command(name="info", description='Інформація про бота та його розробника')
	async def info(self,ctx: discord.ApplicationContext):
		embed= discord.Embed(title='Про Radio UA')
		embed.description = ("###🤖 | Бот\n> Бот вміє вмикати українське радіо у голосовому каналі\n"
							 "###🐚 | Розробник\n> Розробив його 16-и річний програміст з Хмельницького - оптиміст, ось доречі мій сервер ;) https://discord.gg/RqTVhRD5vR\n"
							 "###💖 | Дякуємо що користуєтесь нашим ботом!\n> На нашому сервері можете поглянути на інших наших ботів, а також отримати фідбек щодо цього бота\n")
		embed.colour = discord.Colour.purple()
		embed.set_thumbnail(url=self.bot.user.avatar.url)
		await ctx.respond(embed=embed)
	@commands.slash_command(name="radio_stop", description="🛸 | Зупинити радіо") # we can add event listeners to our cog
	async def radio_stop(self,ctx: discord.ApplicationContext):

		voice_channel: discord.VoiceChannel = ctx.author.voice.channel
		if voice_channel==None:
			await ctx.respond("Зайдіть у голосовий канал!")
			return
		await ctx.respond("Радіо вимкнено 🛸")
		await ctx.voice_client.disconnect()
	@commands.slash_command(name="radio", description="🛸 | Запустити радіо") # we can add event listeners to our cog
	async def radio(self,ctx: discord.ApplicationContext, radio_station=discord.Option(str, choices=list(radio_list.keys()))):
		stream_url = radio_list[radio_station]

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