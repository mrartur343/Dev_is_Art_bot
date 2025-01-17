import json
import discord
from discord.ext import commands, pages
from modules import vote_systems



vote_embed = discord.Embed(title='Вибори ради I тур')
vote_embed.description = ("Виберіть 2 кандидатів, вибір можна змінити, неможна голосувати за себе")
vote_embed.colour = discord.Colour.purple()
vote_embed.set_image(
	url='https://cdn.discordapp.com/attachments/1208129686572638214/1267213123555823777/9.png?ex=66a7f7b0&is=66a6a630&hm=d420ac2dab972e393c8663a70dbe3c348990300d3838f67ac12ad7230daaba77&')


class VotingMenu(discord.ui.View):
	@discord.ui.select( # the decorator that lets you specify the properties of the select menu
		placeholder = "Виберіть 2 людини", # the placeholder text that will be displayed if nothing is selected
		min_values = 2, # the minimum number of values that must be selected by the users
		max_values = 2, # the maximum number of values that can be selected by the users
		custom_id='s',
		options = [ # the list of options from which users can choose, a required field
			discord.SelectOption(
				label="0. @abemys_5272",
				description="С.О.Л.О. (лівий)",
				value="0"
			),
			discord.SelectOption(
				label="1. @q7d19b_",
				description="Націонал-демократична партія (правий)",
				value="1"
			),
			discord.SelectOption(
				label="2. @.rykhart",
				description="Націонал-демократична партія (правий)",
				value="2"
			),
			discord.SelectOption(
				label="3. @yanekyz",
				description="Націонал-демократична партія (праий)",
				value="3"
			),
			discord.SelectOption(
				label="4. @.d.k._",
				description="Націонал-демократична партія (центрист)",
				value="4"
			),
			discord.SelectOption(
				label="5. @jjhjahd69",
				description="Вітряна гвардія (правий)",
				value="5"
			),
			discord.SelectOption(
				label="6. @redwolf_ua",
				description="Вітряна гвардія (правий)",
				value="6"
			),
			discord.SelectOption(
				label="7. @ukrainetop",
				description="Вітряна гвардія (правий)",
				value="7"
			),
			discord.SelectOption(
				label="8. @jyemuksya",
				description="Вітряна гвардія (правий)",
				value="8"
			)
		]
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction): # the function called when the user is done selecting options
		selected_str = ''

		council_select_ids = [
			965216192530890853,
			1154105417283150034,
			950516894102855721,
			1014161256019664977,
			670639885433962496,
			820635779721986150,
			736910435747364866,
			821004404664172596,
			508322094673690655
		]



		choices_int = [int(select.values[0])]

		for ch in choices_int:
			selected_str += f"\n- <@{council_select_ids[ch]}>"
			if council_select_ids[ch] == interaction.user.id:
				await interaction.respond('Неможливо проголосувати за себе', ephermal=True)
				return
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