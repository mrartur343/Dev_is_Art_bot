import json
import typing

import discord
from discord.ext import commands, pages
from modules import store_controller as shop_controll




class BuyItemButton(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View

	def __init__(self, pages: pages.Paginator, *args, **kwargs):
		super().__init__(*args)
		if pages!=None:
			self.paginator = pages

	@discord.ui.button(style=discord.ButtonStyle.green,custom_id="buy_button",label='Buy', emoji="🛒") # Create a button with the label "😎 Click me!" with color Blurple
	async def button_callback(self, button, interaction):
		shop_msg = self.paginator.message
		if shop_msg==None:
			return
		msg: discord.Message = shop_msg
		name = msg.embeds[0].title.split(" | ")[1].split('**')[0]

		try:
			item = shop_controll.get_item(name)
		except:
			await interaction.respond("Такого предмета не існує 0_о")
			return
		print(name)
		result = shop_controll.buy_item(item["name"], interaction.user.id)
		if result == 'cash':
			await interaction.respond("Недостатньо коштів", ephemeral=True)
		elif result == 'item':
			await interaction.respond("Такого предмета не існує 0_о", ephemeral=True)
		else:
			await interaction.respond(f"Предмет **`{item['name']}`** успішно куплено", ephemeral=True)



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

options_labels = shop_controll.options_labels




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
		options.append(discord.SelectOption(label=option,emoji=sorted_emojies[i]))

	@discord.ui.select( # the decorator that lets you specify the properties of the select menu
		placeholder = "🎨 | Магазин кольорів", # the placeholder text that will be displayed if nothing is selected
		min_values = 1, # the minimum number of values that must be selected by the users
		max_values = 1, # the maximum number of values that can be selected by the users
		options = options
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction): # the function called when the user is done selecting options
		try:
			item = shop_controll.get_item(select.values[0])
		except:
			await interaction.respond("Такого предмета не існує 0_о")
			return
		result = shop_controll.buy_item(item["name"], interaction.user.id)
		if result == 'cash':
			await interaction.respond("Недостатньо коштів", ephemeral=True)
		elif result == 'item':
			await interaction.respond("Такого предмета не існує 0_о", ephemeral=True)
		else:
			await interaction.respond("Предмет успішно куплено", ephemeral=True)

class ColorSelect(discord.ui.View):


	def __init__(self,member:discord.Member,color_roles: typing.Dict[str, discord.Role], *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		user_items: dict = shop_controll.get_user_items(member.id)

		self.member_colors = user_items
		self.options=[]

		select_menu: discord.ui.Select = super().get_item('select')
		select_menu.options = []
		print(user_items.keys())
		print(options_labels)
		for name in list(user_items.keys()):
			if name in options_labels:
				select_menu.options.append(
					discord.SelectOption(label=name, emoji=self.sorted_emojies[options_labels.index(name)]))

		select_menu.options.append(discord.SelectOption(label="Очистити колір", emoji="🧼", value='clear'))

		self.member = member
		self.color_roles = color_roles



	with open('emojies.json', 'r') as file:
		emojies = json.loads(file.read())
	ids =[]
	for emoji in emojies:
		emoji: str
		ids.append(int(emoji.split(':')[1].split('tile')[-1]))

	sorted_emojies = [None]*16

	for i,id_e in enumerate(ids):
		sorted_emojies[id_e]=emojies[i]


	items = shop_controll.get_items()
	color_items = []



	options = []
	options.append(discord.SelectOption(label="Очистити колір",emoji="🧼",value='clear'))


	@discord.ui.select( # the decorator that lets you specify the properties of the select menu
		placeholder = "🎨 | Вибрати колір", # the placeholder text that will be displayed if nothing is selected
		min_values = 1, # the minimum number of values that must be selected by the users
		max_values = 1, # the maximum number of values that can be selected by the users
		options = options,
		custom_id='select'
	)
	async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction): # the function called when the user is done selecting options
		for role in self.color_roles.values():
			if role in interaction.user.roles:
				await interaction.user.remove_roles(role)
		if select.values[0]=='clear':
			await interaction.respond(f"Успішно очищено ваш колір",
									  ephemeral=True)
			return

		await interaction.user.add_roles(self.color_roles[select.values[0]])
		await interaction.respond(f"Успішно змінено колір на {self.color_roles[select.values[0]].mention}", ephemeral=True)

class Store(commands.Cog): # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot): # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		self.color_roles = {}

		server = await self.bot.fetch_guild(1208129686031310848)

		all_roles: typing.Dict[str,discord.Role] = {}

		for role in await server.fetch_roles():
			if "・" in role.name:
				all_roles[role.name.split("・")[2]]=role

		for i,color_name in enumerate(options_labels):
			self.color_roles[color_name]=all_roles[color_name]

		print(self.color_roles)

	item_commands = discord.SlashCommandGroup(name='item', description='дії з предметами')

	@item_commands.command(name= 'shop')
	async def collection_list(self, ctx):
		items = shop_controll.get_items()
		if len(items)==0:
			await ctx.respond("Поки-що жодного предмета!")
			return
		custom_items = []
		color_items = []

		for i,item in enumerate(items):
			items_embed = discord.Embed()
			n = '\n'
			print(item)
			icon  ="📦"
			if item['name'] in options_labels:
				icon="🎨"
			items_embed.title=f"**{icon} | {item['name']}**"
			items_embed.description = f"{item['description'].replace('&', n)}\n> - Автор: <@{item['author_id']}>\n> - Ціна: {item['price']}\n> - ID: {i}"

			if icon=='📦':
				custom_items.append(items_embed)
			if icon=='🎨':
				color_items.append(items_embed)

		buttons = [
			pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
			pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
			pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
			pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
			pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
		]
		msg: discord.Interaction = await ctx.respond("load...")
		custom_view: BuyItemButton = BuyItemButton(None)


		page_groups = [
			pages.PageGroup(
				pages=custom_items,
				label="📦 | Кастомні предмети",
				description="Предмети створенні учасниками серверу. Для колекціонування",
				custom_buttons=buttons,
				use_default_buttons=False,
				custom_view=custom_view
			),
			pages.PageGroup(
				pages=color_items,
				label="🎨 | Фарби",
				description="Фарби дають можливість у будь-який момент пофарбувати ваш нікнейм",
				custom_buttons=buttons,
				use_default_buttons=False,
				custom_view=custom_view
			),
		]
		paginator: pages.Paginator = pages.Paginator(
			pages=page_groups,
			show_indicator=True,
			use_default_buttons=False,
			custom_buttons=buttons,
			timeout=None,
			show_menu=True,
			custom_view=custom_view
		)
		custom_view.paginator = paginator
		await paginator.respond(msg, ephemeral=False)
		await paginator.update(custom_view=custom_view)

	@item_commands.command() # we can also add application commands
	async def create(self, ctx: discord.ApplicationContext):
		await ctx.send_modal(ItemForm(title='Створити предмет'))

	@commands.has_permissions(administrator=True)
	@item_commands.command() # we can also add application commands
	async def shop_colors(self, ctx: discord.ApplicationContext):
		await ctx.respond(view=StoreSelect(timeout=None))
	@item_commands.command() # we can also add application commands
	async def select_color(self, ctx: discord.ApplicationContext):

		await ctx.respond(view=ColorSelect(member=ctx.user, color_roles=self.color_roles))

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