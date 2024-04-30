import discord
from discord.ext import commands

class WithoutCategory(commands.Cog): # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot): # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@discord.slash_command()
	async def info(self,ctx: discord.ApplicationContext):
		embed = discord.Embed(title=f"Info", description="Інформація про бота",
							  color=discord.Colour.purple())
		embed.add_field(name='📆Created On', value=f"<t:{round(self.bot.user.created_at.timestamp())}:F>", inline=True)
		owner = await (self.bot.fetch_user(658217734814957578))
		embed.add_field(name='👑Owner', value=f"{owner}", inline=True)

		if ctx.guild.icon!=None:
			embed.set_thumbnail(url=ctx.guild.icon.url)
		embed.set_footer(text="Dev is Art!")
		icon_url = ''
		if self.bot.user.avatar!=None:
			icon_url = self.bot.user.avatar.url
		embed.set_author(name=f'{self.bot.user.name}',
		icon_url = icon_url)
		await ctx.respond(embed=embed)

	@discord.slash_command()
	async def server(self,ctx: discord.ApplicationContext):
		embed = discord.Embed(title=f"{ctx.guild.name} Info", description="Information of this Server",
							  color=discord.Colour.blue())
		embed.add_field(name='🆔Server ID', value=f"{ctx.guild.id}", inline=True)
		embed.add_field(name='📆Created On', value=f"<t:{round(ctx.guild.created_at.timestamp())}:F>", inline=True)
		embed.add_field(name='👑Owner', value=f"{ctx.guild.owner.mention}", inline=True)
		embed.add_field(name='👥Members', value=f'{ctx.guild.member_count} Members', inline=True)
		members = ctx.guild.fetch_members()
		humans = []
		async for member in members:
			if not member.bot:
				humans.append(member)
		embed.add_field(name='💖Humans', value=f'{len(humans)} Humans', inline=True)
		embed.add_field(name='💬Channels',
						value=f'{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice',
						inline=True)
		if ctx.guild.icon!=None:
			embed.set_thumbnail(url=ctx.guild.icon.url)
		embed.set_footer(text="Dev is Art!")
		icon_url = ''
		if ctx.author.avatar!=None:
			icon_url = ctx.author.avatar.url
		embed.set_author(name=f'{ctx.author.name}',
		icon_url = icon_url)
		await ctx.respond(embed=embed)

def setup(bot): # this is called by Pycord to setup the cog
	bot.add_cog(WithoutCategory(bot)) # add the cog to the bot