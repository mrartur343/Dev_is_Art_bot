import json
import discord
from discord.ext import commands, pages
from modules import vote_systems






class MyView(discord.ui.View):
	@discord.ui.select( # the decorator that lets you specify the properties of the select menu
		placeholder = "Виберіть 3 людей", # the placeholder text that will be displayed if nothing is selected
		min_values = 3, # the minimum number of values that must be selected by the users
		max_values = 3, # the maximum number of values that can be selected by the users
		custom_id='s',
		options = [ # the list of options from which users can choose, a required field
			discord.SelectOption(
				label="@artemcurious",
				description="Партія #newdevisart",
				value="0"
			),
			discord.SelectOption(
				label="@yanekyz",
				description="Партія #newdevisart",
				value="1"
			),
			discord.SelectOption(
				label="@optymist",
				description="Партія #newdevisart",
				value="2"
			),
			discord.SelectOption(
				label="@q7d19b_",
				description="Партія #newdevisart",
				value="3"
			),
			discord.SelectOption(
				label="@chickenganfan228",
				description="Незалежний",
				value="4"
			),
			discord.SelectOption(
				label="@m1b0t",
				description="Незалежний",
				value="5"
			),
			discord.SelectOption(
				label="@playushki",
				description="Коаліція z.I.g",
				value="6"
			),
			discord.SelectOption(
				label="@cap_banana",
				description="Коаліція z.I.g",
				value="7"
			)
		]
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction): # the function called when the user is done selecting options
		selected_str = ''

		council_select_ids = [591690683509768223,
		1014161256019664977,
		658217734814957578,
		1154105417283150034,
		499940320088293377,
		804694699364319253,
		654019681534869505,
		767783132031352884]





		choices_int = (int(select.values[0]), int(select.values[1]), int(select.values[2]))

		for ch in choices_int:
			selected_str += f"\n- <@{council_select_ids[ch]}>"
			if interaction.user.id==council_select_ids[ch]:
				await interaction.respond(f"Ви не можете обрати самого себе!", ephemeral=True)
				break
		else:
			vote_systems.vote(interaction.user.id, list(choices_int))


			await interaction.respond(f"Ви обрали: {selected_str}", ephemeral=True)


class VoteSystem(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	events_group = discord.SlashCommandGroup(name='vote')


	@events_group.command(name = 'start_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def start_vote(self, ctx:discord.ApplicationContext):

		embed = discord.Embed(title='Вибори у раду')
		embed.description = ("Ось й починаються вибори у раду серверу, виберіть 3 кандидата за яких ви проголосуєте, ви маєте право потім змінити свій вибір")
		embed.colour = discord.Colour.purple()
		embed.set_image(url='https://cdn.discordapp.com/attachments/1208129687067303944/1266852165188714606/7.png?ex=66a6a785&is=66a55605&hm=0a77c7e477d06436d2d48c7a10971b3a87c013817376ed619d9f36aa39275e89&')
		await ctx.respond(embed=embed,view=MyView(timeout=None))

	@events_group.command(name = 'update_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def update_vote(self, ctx:discord.ApplicationContext, msg_id: discord.Option(str)):
		embed = discord.Embed(title='Вибори у раду')
		embed.description = ("Ось й починаються вибори у раду серверу, виберіть 3 кандидата за яких ви проголосуєте, ви маєте право потім змінити свій вибір")
		embed.colour = discord.Colour.purple()
		embed.set_image(url='https://cdn.discordapp.com/attachments/1208129687067303944/1266852165188714606/7.png?ex=66a6a785&is=66a55605&hm=0a77c7e477d06436d2d48c7a10971b3a87c013817376ed619d9f36aa39275e89&')



		msg = await ctx.channel.fetch_message(int(msg_id))
		if msg.author.id == self.bot.user.id:
			await msg.edit(embed=embed, view=MyView(timeout=None))

	@events_group.command(name = 'end_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def end_vote(self, ctx:discord.ApplicationContext):
		voices = vote_systems.calculate_voices()

		voice_num= []

		for i in range(8):
			if not (i in voices):
				voices[i]=0
			voice_num.append(voices[i])

		total_voices = sum(voice_num)


		embed = discord.Embed(title='Обрано раду серверу!')
		embed.description = (f"> <@591690683509768223> {round((total_voices/voice_num[0])*100)}%"
							 f"\n> <@1014161256019664977> {round((total_voices/voice_num[1])*100)}%"
							 f"\n> <@658217734814957578> {round((total_voices/voice_num[2])*100)}%"
							 f"\n> <@1154105417283150034> {round((total_voices/voice_num[3])*100)}%"
							 f"\n> <@499940320088293377> {round((total_voices/voice_num[4])*100)}%"
							 f"\n> <@804694699364319253> {round((total_voices/voice_num[5])*100)}%"
							 f"\n> <@654019681534869505> {round((total_voices/voice_num[6])*100)}%"
							 f"\n> <@767783132031352884> {round((total_voices/voice_num[7])*100)}%")
		embed.colour = discord.Colour.purple()
		await ctx.respond(embed=embed)


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(VoteSystem(bot))  # add the cog to the bot