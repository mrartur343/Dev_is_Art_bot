import json
import discord
from discord.ext import commands, pages
from modules import vote_systems



vote_embed = discord.Embed(title='Вибори у раду (Другий тур)')
vote_embed.description = ("Виберіть 1 кандидата, вибір можна змінити, неможна голосувати кандидатам")
vote_embed.colour = discord.Colour.purple()
vote_embed.set_image(
	url='https://cdn.discordapp.com/attachments/1208129686572638214/1267213123555823777/9.png?ex=66a7f7b0&is=66a6a630&hm=d420ac2dab972e393c8663a70dbe3c348990300d3838f67ac12ad7230daaba77&')


class VotingMenu(discord.ui.View):
	@discord.ui.select( # the decorator that lets you specify the properties of the select menu
		placeholder = "Виберіть 1 людину", # the placeholder text that will be displayed if nothing is selected
		min_values = 1, # the minimum number of values that must be selected by the users
		max_values = 1, # the maximum number of values that can be selected by the users
		custom_id='s',
		options = [ # the list of options from which users can choose, a required field
			discord.SelectOption(
				label="@optymist",
				description="Партія #newdevisart",
				value="0"
			),
			discord.SelectOption(
				label="@cap_banana",
				description="Коаліція z.I.g",
				value="1"
			),
			discord.SelectOption(
				label="@playushki",
				description="Коаліція z.I.g",
				value="2"
			)
		]
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction): # the function called when the user is done selecting options
		selected_str = ''

		council_select_ids = [
		658217734814957578,
		654019681534869505,
		767783132031352884]


		if interaction.user.id in council_select_ids:
			await interaction.respond(f"Кандидати немають права голосувати", ephemeral=True)
			return


		choices_int = [int(select.values[0])]

		for ch in choices_int:
			selected_str += f"\n- <@{council_select_ids[ch]}>"
		else:
			vote_systems.vote(interaction.user.id, choices_int)


			await interaction.respond(f"Ви обрали: {selected_str}", ephemeral=True)


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

		for i in range(3):
			if not (i in voices):
				voices[i]=0
			voice_num.append(voices[i])

		total_voices = sum(voice_num)


		embed = discord.Embed(title='Дообрано третього радника серверу!')
		embed.description = (
							 f"> <@658217734814957578> {round((voice_num[0]/total_voices)*100)}%"
							 f"\n> <@654019681534869505> {round((voice_num[1]/total_voices)*100)}%"
							 f"\n> <@767783132031352884> {round((voice_num[2]/total_voices)*100)}%")
		embed.colour = discord.Colour.purple()
		await ctx.respond(embed=embed)


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(VoteSystem(bot))  # add the cog to the bot