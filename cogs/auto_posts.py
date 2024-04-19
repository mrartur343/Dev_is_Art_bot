import discord
from discord.ext import commands
import datetime
from modules import collections_controller
from cogs import posts

posts_channel_id = 1228087419660800040
class AutoPosts(commands.Cog):

	def __init__(self, bot):
		self.bot: discord.Bot = bot

	@commands.Cog.listener()
	async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
		py_dt = datetime.datetime.now()
		epoch = round(py_dt.timestamp())
		collections_controller.post_append(f"g_{event.guild.id}",event.name,event.description+f"\n> - Початок: <t:{epoch}:R>\n> - #event",img_url=event.cover.url if event.cover!=None else "",author_id=self.bot.user.id)
		await posts.update_channel(await self.bot.fetch_channel(posts_channel_id), event.guild.id)
def setup(bot):
	bot.add_cog(AutoPosts(bot))