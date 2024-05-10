import asyncio
import math
import discord
from discord.ext import commands, pages

from modules import collections_controller


class AppendForm(discord.ui.Modal):
	def __init__(self,collection_name, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.collection_name=collection_name
		self.add_item(discord.ui.InputText(label="Назва"))
		self.add_item(discord.ui.InputText(label="Зміст", style=discord.InputTextStyle.long))
		self.add_item(discord.ui.InputText(label="Автор"))
		self.add_item(discord.ui.InputText(label="Покликання"))

	async def callback(self, interaction: discord.Interaction):
		name = self.children[0].value
		description = self.children[1].value
		author = self.children[2].value
		url = self.children[3].value
		collections_controller.collection_append(self.collection_name,name,description,author,url)
		await interaction.respond(f"Успішно додано **`{name}`** до бази творчості серверу!")
class Collections(commands.Cog): # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot): # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@commands.Cog.listener()

	async def on_thread_create(self,thread: discord.Thread):
		await asyncio.sleep(3)
		collection_name = None
		if thread.parent.id == 1208456905320570910:
			collection_name='poems'
		if thread.parent.id == 1208456988334358569:
			collection_name='arts'
		if thread.parent.id == 1208457109990015046:
			collection_name='games'
		if thread.parent.id == 1227724649639448626:
			collection_name='other'

		if collection_name!=None:
			start_message = thread.last_message
			url = start_message.jump_url
			if len(start_message.attachments) > 0:
				url = start_message.attachments[0].url
			collections_controller.collection_append(collection_name, thread.name, start_message.content,
													 start_message.author.mention, url)
			await thread.send(f"Успішно додано **`{thread.name}`** до бази творчості серверу!")

	@commands.Cog.listener()
	async def on_ready(self):
		print("Collections: ON")
	collection = discord.SlashCommandGroup("collection", "Операції з колекціями творчості з якою ділились різні учасники цього серверу")
	@collection.command(name= 'list')
	async def collection_list(self, ctx,
							  selected: discord.Option(str,name="collection", choices=["poems", "arts", "games", "other"]), page:discord.Option(int, required=False)):
		items = collections_controller.get_collection(selected)
		if len(items)==0:
			await ctx.respond("Поки-що жодного об'єкта у цій колекції!")
			return
		items_pages = []
		for item in items:
			items_embed = discord.Embed()
			if selected == "arts":
				print(item)
				items_embed.set_image(url=item["url"])
			items_embed.url = item["url"]
			n = '\n'
			items_embed.title=f"**{item['name']}**"
			items_embed.description = f"{item['description'].replace('&', n)}\n> - Автор: {item['author']}"

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

	@collection.command(name="append_from_post")
	@commands.has_permissions(administrator=True)
	async def append_from_post(self,ctx: discord.ApplicationContext,
							   collection_name: discord.Option(str, choices=["poems", "arts", "games", "other"]), thread = discord.Option(discord.Thread)):
		thread: discord.Thread
		start_message =  (await thread.history(limit=1,oldest_first=True).flatten())[0]
		url = start_message.jump_url
		if len(start_message.attachments)>0:
			url = start_message.attachments[0].url
		collections_controller.collection_append(collection_name,thread.name,start_message.content,start_message.author.mention,url)
		await ctx.respond(f"Успішно додано **`{thread.name}`** до бази творчості серверу!")

	@collection.command(name="append_form")
	@commands.has_permissions(administrator=True)
	async def append_form(self,ctx: discord.ApplicationContext,
						  collection_name: discord.Option(str, choices=["poems", "arts", "games", "other"])):
		modal = AppendForm(title="Append Form",collection_name=collection_name)
		await ctx.send_modal(modal)

	@collection.command()
	@commands.has_permissions(administrator=True)
	async def append_manual(self,ctx: discord.ApplicationContext,
							collection_name: discord.Option(str, choices=["poems", "arts", "games", "other"]),
							name: discord.Option(str),
							description: discord.Option(str),
							author: discord.Option(str),
							url: discord.Option(str),
							):
		collections_controller.collection_append(collection_name,name,description,author,url)
		await ctx.respond(f"Успішно додано **`{name}`** до бази творчості серверу!")




async def setup(bot): # this is called by Pycord to setup the cog
	await bot.add(Collections(bot)) # add the cog to the bot