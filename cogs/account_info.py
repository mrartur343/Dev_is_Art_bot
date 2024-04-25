import json
import typing
import jmespath
import discord
from discord.ext import commands
from modules import store_controller as shop_controll
from modules import account_controll

options_labels = shop_controll.options_labels
class AddEventPoints(discord.ui.Modal):
	def __init__(self, member: discord.Member, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self.member = member
		self.add_item(discord.ui.InputText(label="Кількість івент поінтів"))
		self.add_item(discord.ui.InputText(label="Коментар"))

	async def callback(self, interaction: discord.Interaction):
		amount =self.children[0].value
		comment =self.children[1].value
		shop_controll.change_cash(self.member.id, int(amount))
		await interaction.respond(f"Успішно змінено кількість івент поінтів {self.member} на {'+' if int(amount)>0 else ''}{amount}", ephemeral=True)
		await self.member.send(f"Кількість ваших івент поінтів на сервер Dev is Art змінили на {'+' if int(amount)>0 else ''}{amount}\n> {comment}")


class AdminPanel(discord.ui.View):
	def __init__(self, *items):
		super().__init__(*items)

	achievements = account_controll.all_achievements()

	options = []
	options.append(discord.SelectOption(label='Створити ачівку', value='achievement_create'))

	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="Вибрати дію",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		max_values=1,  # the maximum number of values that can be selected by the users
		options=options
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):  # the function called when the user is done selecting options
		if select.values[0] == 'achievement_create':
			await interaction.response.send_modal(CreateAchievement(title='Створити ачівку'))
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
			achievements_listed += f"\n- {achievements[v]['name']}"

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

	sorted_emojies = [None] * 16

	for i, id_e in enumerate(ids):
		sorted_emojies[id_e] = emojies[i]

	user = shop_controll.get_user_cash(member.id)
	user_items: dict = shop_controll.get_user_items(member.id)

	embed = discord.Embed(title=member.name)

	embed.add_field(name="Загальні відомості", inline=False, value='---')
	embed.add_field(name="> <:e_:1232623079637778482> | Івент поінти: ", inline=False, value=f"> {user['cash']}")
	embed.add_field(name="Інвентар", inline=False,
					value='---\n`Змінити колір: `</item select_color:1232018128507240499>')

	for k, v in user_items.items():
		if k in self.color_roles.keys():
			k = f'> 🖌️ | ' + self.color_roles[k].mention
		else:
			k = '> 📦 | ' + k

		embed.add_field(name="", value=f"{k}:\n> {v}", inline=False)
		embed.add_field(name="", value="", inline=False)

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

	account_commands = discord.SlashCommandGroup(name='account',
												 description="Повна інформаці про ваш акаунт на сервер: ачівки, івенти, івент поінти та інвентар")

	@account_commands.command(name='me')  # we can also add application commands
	async def about_me(self, ctx: discord.ApplicationContext):
		await ctx.respond(embeds=await profile_embed(self, ctx.author))

	@discord.user_command(name='Акаунт серверу')
	async def about_member(self, ctx, member: discord.Member):
		await ctx.respond(embeds=await profile_embed(self, member))

	@discord.user_command(name='Add event points (для адмінів)')
	@commands.has_permissions(administrator=True)
	async def add_event_point(self, ctx: discord.ApplicationContext, member: discord.Member):
		await ctx.send_modal(AddEventPoints(member, title='Add Event Points'))

	@commands.has_permissions(administrator=True)
	@discord.user_command(name='Add achievements (для адмінів)')
	async def add_achievement(self, ctx, member: discord.Member):

		await ctx.respond(view=AchievementsAdd(member), ephemeral=True)

	@commands.Cog.listener()  # we can add event listeners to our cog
	async def on_message(self, msg: discord.Message):  # this is called when a member joins the server
		all_id = account_controll.get_all_id()
		if msg.content=='admin_panel':
			await msg.channel.send(view=AdminPanel())

		for mention in msg.mentions:
			if (len(msg.content)-1<=len(mention.mention)) and (msg.content.endswith('p')):
				member = mention
				await msg.channel.send(embeds=await profile_embed(self,member))



	@commands.Cog.listener()  # we can add event listeners to our cog
	async def on_ready(self):  # this is called when a member joins the server
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


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(Account(bot))  # add the cog to the bot
