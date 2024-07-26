import json
import discord
from discord.ext import commands, pages
from modules import vote_systems





class VoteView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
	@discord.ui.button(label="Міша @abemys_5272", style=discord.ButtonStyle.blurple) # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button, interaction: discord.Interaction):
		vote_systems.vote(interaction.user.id, 0)
		await interaction.response.send_message("Ви проголосували за Міша @abemys_5272, якщо ви передумали то просто виберіть інший варіант.") # Send a message when the button is clicked

	@discord.ui.button(label="Плашка @playushki", style=discord.ButtonStyle.red) # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback2(self, button, interaction: discord.Interaction):
		vote_systems.vote(interaction.user.id, 1)
		await interaction.response.send_message("Ви проголосували за Плашка @playushki, якщо ви передумали то просто виберіть інший варіант.") # Send a message when the button is clicked


class InterEvents(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	events_group = discord.SlashCommandGroup(name='events')


	@events_group.command(name = 'start_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def start_vote(self, ctx:discord.ApplicationContext):
		embed = discord.Embed(title='Другий тур виборів')
		embed.description = ("Ось й починається другий тур виборів президента серверу. Оберіть 1 з 2 кандидатів:"
		                     "\n> :femboy: Міша @abemys_5272"
		                     "\n> :zIg: Плашка @playushki")
		embed.colour = discord.Colour.purple()
		await ctx.respond(embed=embed,view=VoteView())

	@events_group.command(name = 'end_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def end_vote(self, ctx:discord.ApplicationContext):
		voices = vote_systems.calculate_voices()
		v0 = voices[0]
		v1 = voices[1]
		embed = discord.Embed(title='Обрано президента серверу!' if v0!=v1 else 'Сталась неочікувана ситуація')
		embed.description = (f"> :femboy: Міша @abemys_5272 {round((v0/(v0+v1))*100)}%"
		                     f"\n> :zIg: Плашка @playushki {round((v1/(v0+v1))*100)}%")
		embed.colour = discord.Colour.purple()
		await ctx.respond(embed=embed)


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(InterEvents(bot))  # add the cog to the bot