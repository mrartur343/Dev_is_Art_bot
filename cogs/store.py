import json

import discord
from discord.ext import commands, pages
from modules import store_controller as shop_controll

class ItemForm(discord.ui.Modal):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.add_item(discord.ui.InputText(label="Назва", style=discord.InputTextStyle.short))
		self.add_item(discord.ui.InputText(label="Ціна", style=discord.InputTextStyle.short))
		self.add_item(discord.ui.InputText(label="Опис", style=discord.InputTextStyle.multiline))

	async def callback(self, interaction: discord.Interaction):
		name = self.children[0].value
		price = self.children[1].value
		description = self.children[2].value

		try:
			shop_controll.item_create(name, int(price),description, interaction.user.id)
			await interaction.respond(f"Успішно додано **`{name}`**!")
		except:
			await interaction.respond(f"Помилка ❌")



options_labels = [

	"Тінь"
	,

	"Виноград"
	,

	"Невизначеність"
	,

	"Червоне полум'я"
	,

	"Чорне море"
	,

	"Діамант"
	,

	"Сніжок"
	,

	"Квітка"
	,

	"Хвоя"
	,

	"Великодка"
	,

	"Левада"
	,

	"Палючий пісок"
	,

	"Гарбуз"
	,

	"Вечірнє небо"
	,

	"Лимон"
	,

	"Світло"

]
class StoreSelect(discord.ui.View):
	with open('emojies.json', 'r') as file:
		emojies = json.loads(file.read())
	ids =[]
	for emoji in emojies:
		emoji: str
		ids.append(int(emoji.split(':')[1].split('tile')[-1]))

	sorted_emojies = [None]*16

	for i,id_e in enumerate(ids):
		sorted_emojies[id_e]=emojies[i]



	options = []
	for i,option in enumerate(options_labels):
		options.append(discord.SelectOption(label=option, value=str(i),emoji=sorted_emojies[i]))

	@discord.ui.select( # the decorator that lets you specify the properties of the select menu
		placeholder = "Магазин кольорів", # the placeholder text that will be displayed if nothing is selected
		min_values = 1, # the minimum number of values that must be selected by the users
		max_values = 1, # the maximum number of values that can be selected by the users
		options = options
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction): # the function called when the user is done selecting options
		await interaction.response.send_message(f"{select.values[0]}!", ephemeral=True)

class Store(commands.Cog): # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot): # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	item_commands = discord.SlashCommandGroup(name='item', description='дії з предметами')

	@item_commands.command(name= 'shop')
	async def collection_list(self, ctx):
		items = shop_controll.get_items()
		if len(items)==0:
			await ctx.respond("Поки-що жодного предмета!")
			return
		items_pages = []
		for i,item in enumerate(items):
			items_embed = discord.Embed()
			n = '\n'
			print(item)
			items_embed.title=f"**{item['name']}**"
			items_embed.description = f"{item['description'].replace('&', n)}\n> - Автор: <@{item['author_id']}>\n> - Ціна: {item['price']}\n> - ID: {i}"

			items_pages.append(items_embed)



		buttons = [
			pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
			pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
			pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
			pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
			pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
		]

		paginator: pages.Paginator = pages.Paginator(
			pages=items_pages,
			show_indicator=True,
			use_default_buttons=False,
			custom_buttons=buttons,
		)
		await paginator.respond(ctx.interaction, ephemeral=False)

	@item_commands.command() # we can also add application commands
	async def create(self, ctx: discord.ApplicationContext):
		await ctx.send_modal(ItemForm(title='Створити предмет'))
	@item_commands.command() # we can also add application commands
	async def shop2(self, ctx: discord.ApplicationContext):
		await ctx.send_modal(ItemForm(title='Створити предмет'))
	@item_commands.command() # we can also add application commands
	async def inventory(self, ctx: discord.ApplicationContext):
		user  =shop_controll.get_user_cash(ctx.author.id)
		user_items:dict  =shop_controll.get_user_items(ctx.author.id)

		embed = discord.Embed(title='Інвентар', description=f"Ваш баланс: {user['cash']}")
		for k,v in user_items.items():
			embed.add_field(name =k+": ",value=v,inline=True)

		await ctx.respond(embed=embed)

	@discord.user_command(name='Check Balance')
	async def balance(self, ctx: discord.ApplicationContext, member: discord.Member):
		user  =shop_controll.get_user_cash(member.id)
		embed = discord.Embed(title=f'Баланс @{member.name}', description=str(user["cash"]))
		await ctx.respond(embed=embed, ephemeral=True)

	@item_commands.command() # we can also add application commands
	async def buy(self,ctx:discord.ApplicationContext, id: discord.Option(int)):
		all_items = shop_controll.get_items()
		try:
			item = all_items[id]
		except:
			await ctx.respond("Такого предмета не існує 0_о")
			return
		result = shop_controll.buy_item(item["name"],ctx.author.id)
		if result=='cash':
			await ctx.respond("Недостатньо коштів")
		elif result=='item':
			await ctx.respond("Такого предмета не існує 0_о")
		else:
			await ctx.respond("Предмет успішно куплено")

def setup(bot): # this is called by Pycord to setup the cog
	bot.add_cog(Store(bot)) # add the cog to the bot