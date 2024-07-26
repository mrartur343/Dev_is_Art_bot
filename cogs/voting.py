import json
import discord
from discord.ext import commands, pages
from modules import vote_systems





class VoteView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
	@discord.ui.button(label="Міша @abemys_5272", style=discord.ButtonStyle.blurple) # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button, interaction: discord.Interaction):
		if interaction.user.id in [965216192530890853,654019681534869505]:
			await interaction.respond("Кандидати не можуть голосувати", ephemeral=True)
			return
		vote_systems.vote(interaction.user.id, 0)
		await interaction.respond("Ви проголосували за Міша <@965216192530890853>, якщо ви передумали то просто виберіть інший варіант.",ephemeral=True) # Send a message when the button is clicked

	@discord.ui.button(label="Плашка @playushki", style=discord.ButtonStyle.red) # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback2(self, button, interaction: discord.Interaction):
		if interaction.user.id in [965216192530890853,654019681534869505]:
			await interaction.respond("Кандидати не можуть голосувати", ephemeral=True)
			return
		vote_systems.vote(interaction.user.id, 1)
		await interaction.respond("Ви проголосували за Плашка <@654019681534869505>, якщо ви передумали то просто виберіть інший варіант.",ephemeral=True) # Send a message when the button is clicked


class VoteSystem(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	events_group = discord.SlashCommandGroup(name='vote')


	@events_group.command(name = 'start_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def start_vote(self, ctx:discord.ApplicationContext, msg_id: discord.Option(str, required=False)=None):

		embed = discord.Embed(title='Другий тур виборів')
		embed.description = ("Ось й починається другий тур виборів президента серверу. Оберіть 1 з 2 кандидатів:"
		                     "\n> <:femboy:1263597372013809757> Міша <@965216192530890853>"
		                     "\n> <:zIg:1263980733219868852> Плашка <@654019681534869505>")
		embed.colour = discord.Colour.purple()
		if msg_id is None:
			await ctx.respond(embed=embed,view=VoteView(timeout=None))
		else:
			msg = await ctx.channel.fetch_message(msg_id)
			if msg.author.id ==self.bot.user.id:
				await msg.edit(embed=embed,view=VoteView(timeout=None))
				await ctx.respond("Оновлено вибори!", ephemeral=True)

	@events_group.command(name = 'end_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def end_vote(self, ctx:discord.ApplicationContext):
		voices = vote_systems.calculate_voices()
		if 0 in voices:
			v0 = voices[0]
		else:
			v0=0
		if 1 in voices:
			v1 = voices[1]
		else:
			v1=0
		embed = discord.Embed(title='Обрано президента серверу!' if v0!=v1 else 'Сталась неочікувана ситуація')
		embed.description = (f"> <:femboy:1263597372013809757> Міша <@965216192530890853> {round((v0/(v0+v1))*100)}%"
		                     f"\n> <:zIg:1263980733219868852> Плашка <@654019681534869505> {round((v1/(v0+v1))*100)}%")
		embed.colour = discord.Colour.purple()
		await ctx.respond(embed=embed)


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(VoteSystem(bot))  # add the cog to the bot