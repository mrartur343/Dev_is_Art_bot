import discord
from discord.ext import commands, pages
from modules import events_controller

class InterEvents(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	events_group = discord.SlashCommandGroup(name='events')


	@events_group.command(name = 'synchronize')  # we can also add application commands
	async def synchronize_all_events(self, ctx:discord.ApplicationContext):



		server_invite = await ctx.channel.create_invite()
		for event in await ctx.guild.fetch_scheduled_events():
			events_controller.add_event(event,server_invite.__str__())

		await ctx.respond("Івенти успішно синхронізовано!")



	@events_group.command(name = 'all')  # we can also add application commands
	async def show_all_events(self, ctx):


		all_events = events_controller.get_all_events()

		events = []

		"""
	
	event_info_dictionary = {
		"id": event_id,
		"name": event_name,
		'desc': event_desc,
		'server_url': event_server_url,
		'server_name': event_server_name,
		'server_img_url': event_server_img_url,
		'created_at': event_created_at,
		'time': event_time,
		'url': event_url,
		'img_url': event_img_url
		
	}"""

		for event in all_events:
			embed = discord.Embed()
			embed.title = event['name']
			embed.description = event['desc']
			embed.description+=(f"\n\n- Створено івент - <t:{event['created_at']}:f>"
			                    f"\n- Початок івенту - <t:{event['time']}:F> (<t:{event['time']}:R>)"
			                    f"\n\n- Сервер, де буде проведено - {event['server_url']}")
			embed.url = event['url']
			embed.set_image(url=event['img_url'])


			embed.set_footer(text=event['server_name'], icon_url=event["server_img_url"])
			events.append(embed)

		paginator = pages.Paginator(pages=events)

		await paginator.respond(ctx.interaction)





def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(InterEvents(bot))  # add the cog to the bot