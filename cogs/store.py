import asyncio
import json
import time
import typing

import discord
from discord.ext import commands, pages
from modules import store_controller as shop_controll

hide_items = [
	"Паутина",
	'Вечірнє небо'
]

options_labels = shop_controll.options_labels



class ColorSelect(discord.ui.View):

	def __init__(self, member: discord.Member, color_roles: typing.Dict[str, discord.Role], *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		user_items: dict = shop_controll.get_user_items(member.id)

		self.member_colors = user_items
		self.options = []

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
	ids = []
	for emoji in emojies:
		emoji: str
		ids.append(int(emoji.split(':')[1].split('tile')[-1]))

	sorted_emojies = [None] * 16

	for i, id_e in enumerate(ids):
		sorted_emojies[id_e] = emojies[i]

	items = shop_controll.get_items()
	color_items = []

	options = []
	options.append(discord.SelectOption(label="Очистити колір", emoji="🧼", value='clear'))

	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="🎨 | Вибрати колір",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		max_values=1,  # the maximum number of values that can be selected by the users
		options=options,
		custom_id='select'
	)
	async def select_callback(self, select: discord.ui.Select,
							  interaction: discord.Interaction):  # the function called when the user is done selecting options
		for role in self.color_roles.values():
			if role in interaction.user.roles:
				await interaction.user.remove_roles(role)
		if select.values[0] == 'clear':
			await interaction.respond(f"Успішно очищено ваш колір",
									  ephemeral=True)
			return

		await interaction.user.add_roles(self.color_roles[select.values[0]])
		await interaction.respond(f"Успішно змінено колір на {self.color_roles[select.values[0]].mention}",
								  ephemeral=True)


class Store(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		self.color_roles = {}

		server = await self.bot.fetch_guild(1208129686031310848)

		all_roles: typing.Dict[str, discord.Role] = {}

		for role in await server.fetch_roles():
			if "・" in role.name:
				all_roles[role.name.split("・")[2]] = role

		for i, color_name in enumerate(options_labels):
			self.color_roles[color_name] = all_roles[color_name]

		print(self.color_roles)



	@commands.slash_command(name='select_color')  # we can also add application commands
	async def select_color(self, ctx: discord.ApplicationContext):

		await ctx.respond(view=ColorSelect(member=ctx.user, color_roles=self.color_roles))
	@commands.slash_command(name='check_voice')  # we can also add application commands
	async def check_voice(self, ctx: discord.ApplicationContext):
		if ctx.voice_client is None:
			await ctx.respond("None")
		else:
			await ctx.respond(ctx.voice_client.channel.id)


async def setup(bot):  # this is called by Pycord to setup the cog
	await bot.add_cog(Store(bot))  # add the cog to the bot