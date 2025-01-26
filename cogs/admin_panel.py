import json
import discord
from discord.ext import commands, pages
from modules import vote_systems



class VoteSystem(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	events_group = discord.SlashCommandGroup(name='vote')


	@events_group.command(name = 'start_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def start_vote(self, ctx:discord.ApplicationContext):

		await ctx.respond(embed=vote_embed, view=VotingMenu(timeout=None))

	@events_group.command(name = 'update_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def update_vote(self, ctx:discord.ApplicationContext, msg_id: discord.Option(str)):


		msg = await ctx.channel.fetch_message(int(msg_id))
		if msg.author.id == self.bot.user.id:
			await msg.edit(embed=vote_embed, view=VotingMenu(timeout=None))

	@events_group.command(name = 'end_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def end_vote(self, ctx:discord.ApplicationContext):
		voices = vote_systems.calculate_voices()

		voice_num= []

		for i in range(9):
			if not (i in voices):
				voices[i]=0
			voice_num.append(voices[i])

		total_voices = sum(voice_num)

		embed = discord.Embed(title='Обрано 2 радників серверу! Президент та рада можуть розпочинати свою діяльність')
		embed.description = (
							 f"> <@965216192530890853> {round((voice_num[0]/total_voices)*100)}%"
							 f"\n> <@1154105417283150034> {round((voice_num[1]/total_voices)*100)}%"
							 f"\n> <@950516894102855721> {round((voice_num[2]/total_voices)*100)}%"
							 f"\n> <@1014161256019664977> {round((voice_num[3] / total_voices) * 100)}%"
							 f"\n> <@670639885433962496> {round((voice_num[4] / total_voices) * 100)}%"
							 f"\n> <@820635779721986150> {round((voice_num[5] / total_voices) * 100)}%"
							 f"\n> <@736910435747364866> {round((voice_num[6] / total_voices) * 100)}%"
							 f"\n> <@821004404664172596> {round((voice_num[7] / total_voices) * 100)}%"
							 f"\n> <@508322094673690655> {round((voice_num[8] / total_voices) * 100)}%")

		embed.colour = discord.Colour.purple()
		await ctx.respond(embed=embed)


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(VoteSystem(bot))  # add the cog to the bot