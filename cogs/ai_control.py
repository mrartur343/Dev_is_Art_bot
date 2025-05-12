import json
import re
import sqlite3
import time

import discord
from discord import InputTextStyle
from discord.ext import commands, tasks
from discord.ui import Modal, InputText


class StrInput(discord.ui.Modal):
	def __init__(self, cog, interaction, *args, **kwargs):
		super().__init__(title='Напишіть лист для ШІ',timeout=None,*args, **kwargs)
		self.cog = cog
		self.interaction = interaction

		self.message_input = InputText(
			label="Повідомлення",
			style=InputTextStyle.paragraph,
			placeholder="Введіть повідомлення...",
			required=True,
			max_length=2000
		)
		self.add_item(self.message_input)

	async def callback(self, interaction: discord.Interaction):
		msg = self.message_input.value
		self.cog.message_cursor.execute(
			"INSERT INTO messages (guild_id, user_id, username, message) VALUES (?, ?, ?, ?)",
			(interaction.guild.id, interaction.user.id, str(interaction.user), msg)
		)
		self.cog.message_db.commit()
		await interaction.respond("✅ Повідомлення збережено!", ephemeral=True)


class ScheduledCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.conn = sqlite3.connect('scheduled_commands.db')
		self.cursor = self.conn.cursor()
		self.cursor.execute('''
			CREATE TABLE IF NOT EXISTS scheduled_commands (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				guild_id INTEGER,
				channel_id INTEGER,
				timestamp INTEGER,
				command TEXT
			)
		''')
		self.conn.commit()

		self.var_db = sqlite3.connect("variables.db")
		self.var_cursor = self.var_db.cursor()
		self.var_cursor.execute('''
			CREATE TABLE IF NOT EXISTS variables (
				guild_id INTEGER,
				name TEXT,
				value TEXT,
				PRIMARY KEY (guild_id, name)
			)
		''')
		self.var_db.commit()

		self.message_db = sqlite3.connect("user_messages.db")
		self.message_cursor = self.message_db.cursor()

		self.message_cursor.execute('''
			CREATE TABLE IF NOT EXISTS messages (
				guild_id INTEGER,
				user_id INTEGER,
				username TEXT,
				message TEXT
			)
		''')
		self.message_db.commit()

		self.check_scheduled_commands.start()

	def cog_unload(self):
		self.check_scheduled_commands.cancel()
		self.conn.close()

	@tasks.loop(seconds=10)
	async def check_scheduled_commands(self):
		now = int(time.time())
		self.cursor.execute('SELECT id, guild_id, channel_id, command FROM scheduled_commands WHERE timestamp <= ?', (now,))
		rows = self.cursor.fetchall()

		for row in rows:
			cmd_id, guild_id, channel_id, command = row
			guild = self.bot.get_guild(guild_id)
			channel = guild.get_channel(channel_id) if guild else None
			if not channel:
				continue
			try:
				await self.execute_command(guild, channel, command)
			except Exception as e:
				await channel.send(f"Помилка при виконанні `{command}`: {e}")
			self.cursor.execute('DELETE FROM scheduled_commands WHERE id = ?', (cmd_id,))
			self.conn.commit()

	async def execute_command(self, guild: discord.Guild, channel, command: str):
		args = command.split()
		if not args:
			await channel.send("Пуста команда.")
			return

		action = args[0]
		match action:
			# --- Канали ---
			case "create_text_channel":
				name = " ".join(args[1:])
				await guild.create_text_channel(name)
				await channel.send(f"Канал `{name}` створено.")

			case "create_voice_channel":
				name = " ".join(args[1:])
				await guild.create_voice_channel(name)
				await channel.send(f"Канал `{name}` створено.")

			case "create_info_channel":
				name = " ".join(args[1:])
			
				# Дозволи: всі не можуть писати
				overwrite = {
					guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
				}
			
				# Створюємо канал з обмеженнями
				info_channel = await guild.create_text_channel(name, overwrites=overwrite)
				await channel.send(f"ℹ️ Інформаційний канал `{name}` створено.")


			case "delete_channel":
				name = " ".join(args[1:])
				ch = discord.utils.get(guild.channels, name=name)
				if ch:
					await ch.delete()
					await channel.send(f"Канал `{name}` видалено.")
				else:
					await channel.send(f"Канал `{name}` не знайдено.")

			case "rename_channel":
				old_name, new_name = args[1], args[2]
				ch = discord.utils.get(guild.channels, name=old_name)
				if ch:
					await ch.edit(name=new_name)
					await channel.send(f"Канал `{old_name}` перейменовано на `{new_name}`.")
				else:
					await channel.send(f"Канал `{old_name}` не знайдено.")

			case "set_channel_topic":
				ch_name = args[1]
				topic = " ".join(args[2:])
				ch = discord.utils.get(guild.channels, name=ch_name)
				if ch and isinstance(ch, discord.TextChannel):
					await ch.edit(topic=topic)
					await channel.send(f"Тема каналу `{ch_name}` оновлена.")
				else:
					await channel.send(f"Канал `{ch_name}` не знайдено або він не текстовий.")
			case "create_category":
				name = " ".join(args[1:])
				await guild.create_category(name)
				await channel.send(f"📁 Категорію `{name}` створено.")

			case "move_channel":
				ch_name, cat_name = args[1], " ".join(args[2:])
				ch = discord.utils.get(guild.channels, name=ch_name)
				category = discord.utils.get(guild.categories, name=cat_name)
				if ch and category:
					await ch.edit(category=category)
					await channel.send(f"📂 Канал `{ch_name}` переміщено до категорії `{cat_name}`.")
				else:
					await channel.send("❌ Канал або категорію не знайдено.")

			# --- Ролі ---
			case "create_role":
				name = " ".join(args[1:])
				await guild.create_role(name=name)
				await channel.send(f"Роль `{name}` створено.")

			case "delete_role":
				name = " ".join(args[1:])
				role = discord.utils.get(guild.roles, name=name)
				if role:
					await role.delete()
					await channel.send(f"Роль `{name}` видалено.")
				else:
					await channel.send(f"Роль `{name}` не знайдено.")

			case "rename_role":
				old_name, new_name = args[1], args[2]
				role = discord.utils.get(guild.roles, name=old_name)
				if role:
					await role.edit(name=new_name)
					await channel.send(f"Роль `{old_name}` перейменовано на `{new_name}`.")
				else:
					await channel.send(f"Роль `{old_name}` не знайдено.")

			# --- Користувачі / ролі ---
			case "add_role":
				member_name = args[1]
				role_name = args[2]
				member = discord.utils.find(lambda m: m.name == member_name, guild.members)
				role = discord.utils.get(guild.roles, name=role_name)
				if member and role:
					await member.add_roles(role)
					await channel.send(f"Роль `{role_name}` додано користувачу `{member_name}`.")
				else:
					await channel.send(f"Не знайдено користувача або ролі.")

			case "remove_role":
				member_name = args[1]
				role_name = args[2]
				member = discord.utils.find(lambda m: m.name == member_name, guild.members)
				role = discord.utils.get(guild.roles, name=role_name)
				if member and role:
					await member.remove_roles(role)
					await channel.send(f"Роль `{role_name}` видалено в користувача `{member_name}`.")
				else:
					await channel.send(f"Не знайдено користувача або ролі.")
			case "dm_user":
				target_name = args[1]
				msg = " ".join(args[2:])

				member = discord.utils.find(lambda m: m.name == target_name or m.display_name == target_name,
				                            guild.members)

				if member:
					try:
						await member.send(msg)
						await channel.send(f"📨 Повідомлення надіслано {member.name}.")
					except discord.Forbidden:
						await channel.send("❌ Не вдалося надіслати повідомлення. Можливо, користувач вимкнув DM.")
				else:
					await channel.send(f"❌ Користувача `{target_name}` не знайдено.")

			# --- Повідомлення ---
			case "send_message":
				if len(args) < 3:
					await channel.send("❌ Використання: send_message НазваКаналу Повідомлення")
					return

				target_channel_name = args[1]
				raw_message = " ".join(args[2:])

				# Пошук каналу за назвою
				target_channel = discord.utils.get(guild.text_channels, name=target_channel_name)
				if not target_channel:
					await channel.send(f"❌ Канал `{target_channel_name}` не знайдено.")
					return

				# Підстановка змінних з бази
				self.var_cursor.execute("SELECT name, value FROM variables WHERE guild_id = ?", (guild.id,))
				variables = dict(self.var_cursor.fetchall())

				for key, value in variables.items():
					raw_message = raw_message.replace(f"{{{key}}}", value)

				await target_channel.send(raw_message)
				await channel.send(f"✅ Повідомлення надіслано до каналу `{target_channel_name}`.")
			# --- Сервер ---
			case "change_server_name":
				new_name = " ".join(args[1:])
				await guild.edit(name=new_name)
				await channel.send(f"Назву сервера змінено на `{new_name}`.")
			case "set_variable":
				if len(args) < 3:
					await channel.send("❌ Формат: `set_variable назва значення`")
					return

				var_name = args[1]
				var_value = " ".join(args[2:])
				self.var_cursor.execute('''
					INSERT INTO variables (guild_id, name, value)
					VALUES (?, ?, ?)
					ON CONFLICT(guild_id, name) DO UPDATE SET value = excluded.value
				''', (guild.id, var_name, var_value))
				self.var_db.commit()
				await channel.send(f"✅ Змінну `{var_name}` встановлено на `{var_value}`.")

			case _:
				await channel.send(f"Невідома команда: `{command}`")
	@commands.has_permissions(administrator=True)
	@discord.slash_command(name="upload_json", description="Завантажити JSON файл з командами")
	async def upload_json(self, ctx: discord.ApplicationContext, file: discord.Attachment):
		if not file.filename.endswith(".json"):
			await ctx.respond("Файл має бути у форматі .json", ephemeral=True)
			return

		try:
			file_bytes = await file.read()
			data = json.loads(file_bytes.decode("utf-8"))

			inserted = 0
			for timestamp_str, command in data.items():
				try:
					timestamp = int(timestamp_str)
					self.cursor.execute('''
						INSERT INTO scheduled_commands (guild_id, channel_id, timestamp, command)
						VALUES (?, ?, ?, ?)
					''', (ctx.guild.id, ctx.channel.id, timestamp, command))
					inserted += 1
				except Exception as e:
					await ctx.channel.send(f"Помилка для `{command}`: {e}")

			self.conn.commit()
			await ctx.respond(f"Успішно додано {inserted} команд з JSON.", ephemeral=True)

		except Exception as e:
			await ctx.respond(f"Помилка при обробці файлу: {e}", ephemeral=True)

	@commands.has_permissions(administrator=True)
	@discord.slash_command(name="list_items", description="Показати всі канали та ролі на сервері")
	async def list_items(self, ctx: discord.ApplicationContext):
		guild = ctx.guild
	
		# Канали
		channel_names = [channel.name for channel in guild.channels]
		channel_list = ", ".join(channel_names) if channel_names else "Немає каналів"
	
		# Ролі
		role_names = [role.name for role in guild.roles if role.name != "@everyone"]
		role_list = ", ".join(role_names) if role_names else "Немає ролей"
	
		# Змінні
		self.var_cursor.execute('SELECT name, value FROM variables WHERE guild_id = ?', (guild.id,))
		variables = self.var_cursor.fetchall()
		if variables:
			var_list = ", ".join(f"{name} = {value}" for name, value in variables)
		else:
			var_list = "Немає змінних"
	
		embed = discord.Embed(title="📋 Інформація сервера", color=discord.Color.blurple())
		embed.add_field(name="Канали", value=channel_list, inline=False)
		embed.add_field(name="Ролі", value=role_list, inline=False)
		embed.add_field(name="Змінні", value=var_list, inline=False)
	
		await ctx.respond(embed=embed, ephemeral=True)

	@commands.has_permissions(administrator=True)
	@discord.slash_command(name="view_scheduled", description="Всі заплановані команди")

	async def view_scheduled(self, ctx: discord.ApplicationContext):
		# Перевірка чи адмін

	
		self.cursor.execute('''
			SELECT timestamp, command, channel_id FROM scheduled_commands
			WHERE guild_id = ?
			ORDER BY timestamp ASC
		''', (ctx.guild.id,))
		rows = self.cursor.fetchall()
	
		if not rows:
			await ctx.respond("🔍 Немає запланованих завдань.", ephemeral=True)
			return
	
		lines = []
		for ts, cmd, ch_id in rows:
			lines.append(f"• ⏰ <t:{ts}:F> в <#{ch_id}> — `{cmd}`")
	
		embed = discord.Embed(
			title="📅 Заплановані завдання",
			description="\n".join(lines),
			color=discord.Color.green()
		)
	
		await ctx.respond(embed=embed, ephemeral=True)
	@commands.has_permissions(administrator=True)
	@discord.slash_command(name="view_submitted", description="Всі останні запитання")

	async def view_submitted(self, ctx: discord.ApplicationContext):

		self.message_cursor.execute(
			"SELECT username, message FROM messages WHERE guild_id = ?", (ctx.guild.id,))
		messages = self.message_cursor.fetchall()

		if not messages:
			await ctx.respond("Немає повідомлень.", ephemeral=True)
			return

		text = "\n".join([f"**{user}** — {msg}" for user, msg in messages])
		embed = discord.Embed(title="📨 Надіслані повідомлення", description=text[:4000], color=discord.Color.blue())

		await ctx.respond(embed=embed, ephemeral=True)

	@discord.slash_command(name="submit_message", description="Написати ШІ повідомлення. Це може бути пропозиція, чи питання, чи ідея")
	async def submit_message(self,  ctx: discord.ApplicationContext):
		await ctx.send_modal(StrInput(self, ctx.interaction))
def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(ScheduledCommands(bot))  # add the cog to the bot
