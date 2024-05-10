import json
import typing
import discord
from discord.ext import commands
from modules import store_controller as shop_controll
from modules import account_controll
import psutil



class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        supportServerButton = discord.ui.Button(label='Мої ачівки', style=discord.ButtonStyle.gray, url='https://discord.com/channels/1208129686031310848/1208129686572638214/1235970207747407932')
        self.add_item(supportServerButton)



options_labels = shop_controll.options_labels
class AdminPanel(discord.ui.View):

	def __init__(self,bot, *args,**kwargs):
		self.bot: discord.Bot = bot

		super().__init__(*args)

	achievements = account_controll.all_achievements()

	options = []
	options.append(discord.SelectOption(label='Створити ачівку', value='achievement_create'))
	options.append(discord.SelectOption(label='Температура', value='temperature'))
	options.append(discord.SelectOption(label='Вимкнути бота', value='poweroff'))

	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="Вибрати дію",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		max_values=1,  # the maximum number of values that can be selected by the users
		options=options
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):  # the function called when the user is done selecting options
		if select.values[0] == 'achievement_create':
			await interaction.response.send_modal(CreateAchievement(title='Створити ачівку'))  # the function called when the user is done selecting options
		elif select.values[0] == 'temperature':
			temperaturs = []

			temperaturs_all = psutil.sensors_temperatures()
			for _, t in temperaturs_all.items():
				for i in t:
					temperaturs.append((i.label, i.current))

			embed = discord.Embed(title='Температури')
			for t in temperaturs:
				embed.add_field(name=t[0],value=f"{t[1]} *C")

			batery: psutil._common.sbattery = psutil.sensors_battery()

			embed.add_field(name='Батарея (заряд)', value = f"{batery.percent}")
			embed.add_field(name='Батарея (увімкнено до мережі)', value = f"{batery.power_plugged}")


			await interaction.respond(embed=embed)
		elif select.values[0] == 'poweroff':
			await interaction.respond("Вимкнення бота!")
			await self.bot.close()
class CreateAchievement(discord.ui.Modal):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)


		self.add_item(discord.ui.InputText(label="Ключ",placeholder="example_key", style=discord.InputTextStyle.short))
		self.add_item(discord.ui.InputText(label="Назва",placeholder="Приклад назви", style=discord.InputTextStyle.singleline))
		self.add_item(discord.ui.InputText(label="Опис",placeholder="Приклад опису\nТут можна кілька рядків", style=discord.InputTextStyle.paragraph))

	async def callback(self, interaction: discord.Interaction):
		if interaction.user.id in [658217734814957578]:
			account_controll.create(self.children[0].value,self.children[1].value,self.children[2].value)
			await interaction.respond(f"Успішно створено ачівку {self.children[1].value} ({self.children[0].value})")
		else:
			await interaction.respond(f"Ти без прав")

class AchievementsAdd(discord.ui.View):
	def __init__(self, member, *items):
		super().__init__(*items)
		self.member: discord.Member = member

		achievements = account_controll.all_achievements()

		options = []
		for achievement, info in achievements.items():
			print(achievement)
			print(info)
			options.append(discord.SelectOption(
				label=info['name'],
				description=info['description'][:100],
				value=achievement
			))

		select_menu: discord.ui.Select = super().get_item('achievement_add')

		select_menu.options = options


	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="Вибери які ачівки додати:",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		options=[],
		custom_id='achievement_add'
	)
	async def select_callback(self, select, interaction):  # the function called when the user is done selecting options
		achievements = account_controll.all_achievements()

		achievements_listed = ""

		for v in select.values:
			account_controll.add_to_member(v, self.member.id)
			achievements_listed += f"\n- **`{achievements[v]['name']}`**\n> {achievements[v]['description']}"
		if self.member.can_send() and self.member.id != 1232014648644206714:
			await self.member.send(
				f"Адміністрація серверу Dev is Art додала вам {len(select.values)} нових ачівок:\n{achievements_listed}")
		await interaction.response.send_message(f"Додано {len(select.values)} ачівок для {self.member.mention}!",
												ephemeral=True)


async def profile_embed(self, member):
	with open('emojies.json', 'r') as file:
		emojies = json.loads(file.read())
	ids = []
	for emoji in emojies:
		emoji: str
		ids.append(int(emoji.split(':')[1].split('tile')[-1]))

	member_colour = discord.Colour.dark_grey()
	for role in member.roles:
		role: discord.Role
		if role in self.color_roles.values():
			member_colour = role.colour

	sorted_emojies = [None] * 16

	for i, id_e in enumerate(ids):
		sorted_emojies[id_e] = emojies[i]

	embed = discord.Embed(title=member.name)

	embed.colour = member_colour


	embed.add_field(name="Ачівки", inline=False, value='---')
	for achievement in account_controll.member_achievements(str(member.id)).values():
		print(achievement)
		embed.add_field(name=achievement["name"], inline=False, value=f">>> {achievement['description']}\n- 👥 {len(achievement['members'])}")
	if len(account_controll.member_achievements(str(member.id)).values())==0:
		embed.add_field(name="*Жодної ачівки*", inline=False, value='')

	if member.avatar != None:
		embed.set_thumbnail(url=member.avatar.url)

	return [embed]


class Account(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot
		self.color_roles = {}

	@commands.slash_command(name='achievements')  # we can also add application commands
	async def achievements(self, ctx: discord.ApplicationContext):
		await ctx.respond(embeds=await profile_embed(self, ctx.author))

	@discord.user_command(name='Ачівки людини')
	async def about_member(self, ctx, member: discord.Member):
		await ctx.respond(embeds=await profile_embed(self, member))
	@commands.has_permissions(administrator=True)
	@discord.user_command(name='Add achievements (для адмінів)')
	async def add_achievement(self, ctx, member: discord.Member):
		await ctx.respond(view=AchievementsAdd(member), ephemeral=True)

	@commands.Cog.listener()  # we can add event listeners to our cog
	async def on_message(self, msg: discord.Message):  # this is called when a member joins the server
		if msg.content=='admin_panel' and msg.author.id ==658217734814957578:
			await msg.channel.send(view=AdminPanel(self.bot))

		for mention in msg.mentions:
			if (len(msg.content)-1<=len(mention.mention)) and (msg.content.endswith('p')):
				member = mention
				await msg.channel.send(embeds=await profile_embed(self,member))



	@commands.Cog.listener()  # we can add event listeners to our cog
	async def on_ready(self):  # this is called when a member joins the server
		guild = await self.bot.fetch_guild(1208129686031310848)
		achievements = account_controll.all_achievements()

		for achievement_key, info in achievements.items():
			if 'other' in info:
				if 'role' in info['other']:
					for member_id in info['members']:
						all_id = []
						for member_g in await guild.fetch_members().flatten():
							all_id.append(member_g.id)
						if member_id in all_id:
							member = await guild.fetch_member(member_id)
							await member.add_roles(guild.get_role(info['other']['role']))
				if 'gift' in info['other']:
					for member_id in info['members']:
						if not info['other']['gift'] in shop_controll.get_user_items(member_id):
							shop_controll.add_item(info['other']['gift'], member_id)


		print("Account: ON")


		self.color_roles = {}



		server = await self.bot.fetch_guild(1208129686031310848)

		all_roles: typing.Dict[str, discord.Role] = {}

		for role in await server.fetch_roles():
			if "・" in role.name:
				all_roles[role.name.split("・")[2]] = role

		for i, color_name in enumerate(options_labels):
			self.color_roles[color_name] = all_roles[color_name]

		print(self.color_roles)
"""
		######

		embed = discord.Embed()

		with open("text.txt", 'r', encoding='utf-8') as file:
			text = file.read()
		embed.description = text
		embed.colour = discord.Colour.from_rgb(111, 103, 118)

		embed.set_image(
			url="https://cdn.discordapp.com/attachments/1208129686572638214/1235974171633254430/ach.png?ex=66365225&is=663500a5&hm=ff69eef38b9ce10e4850b9aaf17068ccb5697bce5e4b0f4d018fa9cd0ff682a7&")

		forum: discord.ForumChannel = await  self.bot.fetch_channel(1235964109942427719)

		await forum.create_thread(name='Ачівки', embed=embed, view=InfoView())

		######"""


def setup(bot: discord.Bot):  # this is called by Pycord to setup the cog
	print("setup")
	bot.add_cog(Account(bot))  # add the cog to the bot
