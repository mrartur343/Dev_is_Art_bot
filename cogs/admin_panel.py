import json
import discord
from discord.ext import commands, pages
from modules import vote_systems




class VoteSystem(commands.Cog):  # create a class for our cog that inherits from commands.Cog
	# this class is used to create a cog, which is a module that can be added to the bot

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot
		self.user_mention_count = {}  # user_id: count

	events_group = discord.SlashCommandGroup(name='vote')


	@events_group.command(name = 'start_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def start_vote(self, ctx:discord.ApplicationContext):

		await ctx.respond(embed=vote_embed, view=VotingMenu(timeout=None))

	@events_group.command(name = 'update_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def update_vote(self, ctx:discord.ApplicationContext, msg_id: discord.Option(str)):


		msg = await ctx.channel.fetch_message(int(msg_id))
		if msg.author.id == self.bot.user.id:
			await msg.edit(embed=vote_embed, view=VotingMenu(timeout=None))

	@events_group.command(name = 'end_vote')
	@commands.has_permissions(administrator=True)# we can also add application commands
	async def end_vote(self, ctx:discord.ApplicationContext):
		voices = vote_systems.calculate_voices()

		voice_num= []

		for i in range(9):
			if not (i in voices):
				voices[i]=0
			voice_num.append(voices[i])

		total_voices = sum(voice_num)

		embed = discord.Embed(title='Обрано 2 радників серверу! Президент та рада можуть розпочинати свою діяльність')
		embed.description = (
							 f"> <@965216192530890853> {round((voice_num[0]/total_voices)*100)}%"
							 f"\n> <@1154105417283150034> {round((voice_num[1]/total_voices)*100)}%"
							 f"\n> <@950516894102855721> {round((voice_num[2]/total_voices)*100)}%"
							 f"\n> <@1014161256019664977> {round((voice_num[3] / total_voices) * 100)}%"
							 f"\n> <@670639885433962496> {round((voice_num[4] / total_voices) * 100)}%"
							 f"\n> <@820635779721986150> {round((voice_num[5] / total_voices) * 100)}%"
							 f"\n> <@736910435747364866> {round((voice_num[6] / total_voices) * 100)}%"
							 f"\n> <@821004404664172596> {round((voice_num[7] / total_voices) * 100)}%"
							 f"\n> <@508322094673690655> {round((voice_num[8] / total_voices) * 100)}%")

		embed.colour = discord.Colour.purple()
		await ctx.respond(embed=embed)

	@commands.slash_command(name="public_opinion", description="Оцінка громадської думки від getter")
	async def public_opinion(self, ctx: discord.ApplicationContext):
		"""Відправляє оцінку громадської думки з останнього повідомлення getter"""
		conn = None
		try:
			from cogs.db_config import DB_NAME
			conn = __import__('sqlite3').connect(DB_NAME)
			cursor = conn.cursor()
			cursor.execute("SELECT content FROM messages_getter ORDER BY timestamp DESC LIMIT 1")
			row = cursor.fetchone()
			if row:
				await ctx.respond(f"Оцінка громадської думки:\n{row[0]}", ephemeral=True)
			else:
				await ctx.respond("Немає повідомлень від getter.", ephemeral=True)
		except Exception as e:
			await ctx.respond(f"Помилка: {e}", ephemeral=True)
		finally:
			if conn:
				conn.close()

	@commands.slash_command(name="owner_plans", description="Останні плани та вказання від owner")
	async def owner_plans(self, ctx: discord.ApplicationContext):
		"""Відправляє останні плани та вказання з останнього повідомлення owner"""
		conn = None
		try:
			from cogs.db_config import DB_NAME
			conn = __import__('sqlite3').connect(DB_NAME)
			cursor = conn.cursor()
			cursor.execute("SELECT content FROM messages_owner ORDER BY timestamp DESC LIMIT 1")
			row = cursor.fetchone()
			if row:
				await ctx.respond(f"Останні плани та вказання owner:\n{row[0]}", ephemeral=True)
			else:
				await ctx.respond("Немає повідомлень від owner.", ephemeral=True)
		except Exception as e:
			await ctx.respond(f"Помилка: {e}", ephemeral=True)
		finally:
			if conn:
				conn.close()

	@commands.slash_command(name="owner_orders", description="Останні накази для ШІ з owner")
	async def owner_orders(self, ctx: discord.ApplicationContext):
		"""Відправляє останні накази для ШІ з json_data з останнього повідомлення owner"""
		conn = None
		try:
			from cogs.db_config import DB_NAME
			import json
			conn = __import__('sqlite3').connect(DB_NAME)
			cursor = conn.cursor()
			cursor.execute("SELECT content FROM messages_owner ORDER BY timestamp DESC LIMIT 1")
			row = cursor.fetchone()
			if row:
				content = row[0]
				# Спробуємо знайти JSON у повідомленні
				json_data = None
				if '```' in content:
					try:
						json_str = content.split('```json' if '```json' in content else '```')[1].split('```')[0]
						json_data = json.loads(json_str)
					except Exception:
						pass
				if json_data:
					await ctx.respond(f"Останні накази для ШІ (owner):\n```json\n{json.dumps(json_data, ensure_ascii=False, indent=2)}\n```", ephemeral=True)
				else:
					await ctx.respond("Не знайдено наказів у форматі JSON в останньому повідомленні owner.", ephemeral=True)
			else:
				await ctx.respond("Немає повідомлень від owner.", ephemeral=True)
		except Exception as e:
			await ctx.respond(f"Помилка: {e}", ephemeral=True)
		finally:
			if conn:
				conn.close()

	@commands.slash_command(name="mod_mentions", description="Всі повідомлення з згадуванням бота для модератора (до 50/день/користувач)")
	async def mod_mentions(self, ctx: discord.ApplicationContext):
		"""Відправляє всі повідомлення з згадуванням бота модератору (до 50 на день на користувача)"""
		import datetime
		import sqlite3
		from cogs.db_config import DB_NAME

		conn = None
		try:
			today = datetime.datetime.utcnow().date()
			bot_id = str(ctx.bot.user.id)
			conn = sqlite3.connect(DB_NAME)
			cursor = conn.cursor()
			cursor.execute("""
				SELECT user_id, username, content, timestamp
				FROM messages_moderator
				WHERE content LIKE ? AND DATE(timestamp) = ?
				ORDER BY timestamp DESC
			""", (f"%<@{bot_id}>%", today))
			rows = cursor.fetchall()

			from collections import defaultdict
			user_msgs = defaultdict(list)
			for user_id, username, content, ts in rows:
				# Лічильник для кожного користувача
				count = self.user_mention_count.get(user_id, 0)
				if count < 50:
					user_msgs[user_id].append((username, content, ts))
					self.user_mention_count[user_id] = count + 1

			if not user_msgs:
				await ctx.respond("Немає повідомлень з згадуванням бота для модератора за сьогодні.", ephemeral=True)
				return

			text = ""
			for user_id, msgs in user_msgs.items():
				text += f"\n**{msgs[0][0]}** (ID: {user_id}):\n"
				for username, content, ts in msgs:
					text += f"- {content}\n"
			await ctx.respond(f"Ось повідомлення з згадуванням бота (до 50 на користувача):\n{text[:4000]}", ephemeral=True)
		except Exception as e:
			await ctx.respond(f"Помилка: {e}", ephemeral=True)
		finally:
			if conn:
				conn.close()
def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(VoteSystem(bot))  # add the cog to the bot