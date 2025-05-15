import json
import os
import random
import sqlite3
import time
from openai import OpenAI

import discord
from discord import InputTextStyle
from discord.ext import commands, tasks
from discord.ui import InputText

AI_LIST = ['getter', 'owner', 'admin', 'eventer', 'moderator']
FIRST_MESSAGE_FILE = 'first_messages/{ai_name}.txt'
API_KEY = os.environ.get('AI_Token')
API_URL = "https://openrouter.ai/api/v1"
DB_NAME = "chat_history.db"
LOG_CHANNEL_ID = 1371537439495028856
GUILD_ID = 1371121463717003344

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get('AI_Token'),
)


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
		await self.cog.send_submit_to_ai(msg, author_nickname=interaction.user.global_name)
		await interaction.respond("✅ Повідомлення надіслано!", ephemeral=True)


class ScheduledCommands(commands.Cog):
	def __init__(self, bot):
		self.bot: discord.Bot = bot
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

		self.api_db = sqlite3.connect(DB_NAME)
		self.api_cursor = self.api_db.cursor()
		self.api_cursor.execute('''
		CREATE TABLE IF NOT EXISTS messages_getter (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			role TEXT NOT NULL,
			content TEXT NOT NULL,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			is_json BOOLEAN DEFAULT 0
		)
	''')
		self.api_cursor.execute('''
		CREATE TABLE IF NOT EXISTS messages_owner (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			role TEXT NOT NULL,
			content TEXT NOT NULL,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			is_json BOOLEAN DEFAULT 0
		)
	''')
		self.api_cursor.execute('''
		CREATE TABLE IF NOT EXISTS messages_admin (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			role TEXT NOT NULL,
			content TEXT NOT NULL,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			is_json BOOLEAN DEFAULT 0
		)
	''')
		self.api_cursor.execute('''
		CREATE TABLE IF NOT EXISTS messages_eventer (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			role TEXT NOT NULL,
			content TEXT NOT NULL,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			is_json BOOLEAN DEFAULT 0
		)
	''')
		self.api_cursor.execute('''
		CREATE TABLE IF NOT EXISTS messages_moderator (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			role TEXT NOT NULL,
			content TEXT NOT NULL,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			is_json BOOLEAN DEFAULT 0
		)
	''')

		for ai_name in AI_LIST:
			if os.path.exists(FIRST_MESSAGE_FILE.format(ai_name=ai_name)):
				with open(FIRST_MESSAGE_FILE.format(ai_name=ai_name), 'r', encoding='utf-8') as f:
					first_message = f.read().strip()

				# Перевіряємо чи не додано вже це повідомлення
				self.api_cursor.execute(f'''
					SELECT 1 FROM messages_{ai_name} 
					WHERE role = 'system' AND content = ? 
					LIMIT 1
				''', (first_message,))

				if not self.api_cursor.fetchone():
					self.api_cursor.execute(f'''
						INSERT INTO messages_{ai_name} (role, content) 
						VALUES (?, ?)
					''', ('system', first_message))

		self.api_db.commit()
		self.api_db.close()



		self.check_scheduled_commands.start()
		self.append_scheduled_commands.start()

		self.message_per_day = 0

	def cog_unload(self):
		self.check_scheduled_commands.cancel()
		self.conn.close()

	@commands.Cog.listener()
	async def on_message(self, msg: discord.Message):
		if not msg.author.bot:
			self.message_per_day +=1

		if random.random()<0.05:
			await self.send_message_to_moderator(msg.content, msg.author.global_name)
	async def send_message_to_moderator(self, submit_text, author_nickname):
		moderator_result = await self.chat_with_deepseek(f'Інструкція: {self.moderator_rules}\n'
				                              f'Зараз: {int(time.time())}\n'
				                      f'Автор: {author_nickname}\n'
				                      f'Повідомлення: {submit_text}', 'moderator')

		await self.upload_scheduled_commands(moderator_result['json_data'])


	@commands.has_permissions(administrator=True)
	@discord.slash_command(name="ai_iter", description="Додати завчасно звіт й запросити команди")
	async def ai_iter(self, ctx: discord.ApplicationContext):
		await ctx.defer()
		await self.append_scheduled_commands()

		embed = discord.Embed(
			title="✅ Успішно надіслано звіт!",
			color=discord.Color.blue()
		)

		await ctx.respond(embed=embed, ephemeral=True)
	async def send_submit_to_ai(self, submit_text, author_nickname):
		await self.chat_with_deepseek(f'автор: {author_nickname}\n'
		                              f'повідомлення: {submit_text}', 'getter')



	async def get_last_message(self, ai_chat):
		"""Повертає останнє повідомлення з історії чату"""
		conn = sqlite3.connect(DB_NAME)
		cursor = conn.cursor()
		
		try:
			# Отримуємо останній запис, відсортувавши за часом або ID
			cursor.execute(f'''
				SELECT role, content, timestamp 
				FROM messages_{ai_chat} 
				ORDER BY timestamp DESC 
				LIMIT 1
			''')
			
			result = cursor.fetchone()
			
			if result:
				return result[1]
			return None
			
		except sqlite3.Error as e:
			print(f"Помилка бази даних: {e}")
			return None
		finally:
			conn.close()
	@tasks.loop(hours=24)
	async def append_scheduled_commands(self):

		guild: discord.Guild = self.bot.get_guild(GUILD_ID)
		if not guild:
			print('Помилка пошуку серверу!')
			return
		true_member_count = len([m for m in guild.members if not m.bot]) if guild else -1

		# Канали
		channel_names = [f"{channel.name} ({f'в категорії {channel.category.name}' if channel.category else ('категорія на сервері' if channel.type==discord.ChannelType.category else 'без категорії')})" for channel in guild.channels]
		channel_list = "\n - ".join(channel_names) if channel_names else "Немає каналів"

		# Ролі
		role_names = [role.name for role in guild.roles if role.name != "@everyone"] if guild else "(Невідомо)"
		role_list = "\n - ".join(role_names) if role_names else "Немає ролей"





		text = await self.get_last_message('getter')

		request_text = (f'1. {self.message_per_day}\n'
						f'2. {true_member_count}\n'
						f'3. \n'
						f'{channel_list}\n'
						f'\n'
						f'4. \n'
						f'{role_list}\n'
						f'\n'
						f'5. \n'
						f'{text}\n'
						f'')

		result = await self.chat_with_deepseek(request_text, 'owner')


		print(result)
		await self.extract_scheduled_commands(result['json_data'])


	async def extract_scheduled_commands(self, json_data: dict):
		if 'admin' in json_data:
			admin_result = await self.chat_with_deepseek(json_data["admin"]+f'\n \n \n timestamp зараз - {int(time.time())}', 'admin')
			await self.upload_scheduled_commands(admin_result['json_data'])

		if 'eventer' in json_data:
			eventer_result = await self.chat_with_deepseek(json_data["eventer"]+f'\n \n \n timestamp зараз - {int(time.time())}', 'eventer')
			await self.upload_scheduled_commands(eventer_result['json_data'])

		if 'moderator' in json_data:
			self.moderator_rules = json_data['moderator']


	@tasks.loop(seconds=10)
	async def check_scheduled_commands(self):
		now = int(time.time())
		self.cursor.execute('SELECT id, guild_id, channel_id, command FROM scheduled_commands WHERE timestamp <= ?', (now,))
		rows = self.cursor.fetchall()

		for row in rows:
			cmd_id, guild_id, channel_id, command = row
			guild = self.bot.get_guild(GUILD_ID)
			channel = await guild.fetch_channel(channel_id) if guild and channel_id else None
			if not channel:
				continue
			try:
				await self.execute_command(guild, channel, command)
			except Exception as e:
				await channel.send(f"Помилка при виконанні `{command}`: {e}")
			self.cursor.execute('DELETE FROM scheduled_commands WHERE id = ?', (cmd_id,))
			self.conn.commit()

	async def extract_json_from_text(self, text):
		"""Спробує знайти та розпарсити JSON у тексті відповіді"""

		print("try to find json:\n "+text+"\n\n\n")
		try:


			# Шукаємо початок JSON (можливі варіанти)
			json_str = text.split('```json')[1].split('```')[0]
			return json.loads(json_str)
		except:
			return None

	async def chat_with_deepseek(self, user_message, ai_chat: str, system_prompt=None):
		"""
		Функція для спілкування з Deepseek з можливістю отримання JSON-даних
		
		:param user_message: Повідомлення користувача
		:param system_prompt: Системний промпт (необов'язковий)
		:param expect_json: Чи очікуємо JSON у відповіді (додає інструкцію до запиту)
		:return: Словник з текстом відповіді та/або розпарсеними JSON-даними
		"""
		conn = sqlite3.connect(DB_NAME)
		cursor = conn.cursor()
		
		try:
			# Додаємо повідомлення користувача до БД
			cursor.execute(
				f"INSERT INTO messages_{ai_chat} (role, content) VALUES (?, ?)",
				("user", user_message)
			)
			conn.commit()
			
			# Отримуємо історію повідомлень
			cursor.execute(f"SELECT role, content FROM messages_{ai_chat} ORDER BY timestamp")
			history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
			
			# Додаємо системний промпт
			if system_prompt:
				history.insert(0, {"role": "system", "content": system_prompt})
			
			# Якщо очікуємо JSON - додаємо інструкцію
			history.append({
					"role": "system",
					"content": "Будь ласка, поверни відповідь у форматі JSON. Дані мають бути валідним JSON у межах текстової відповіді."
				})
			
			# Відправляємо запит

			print(f'Історія {ai_chat}: \n'+ str(history))
			completion = client.chat.completions.create(
				extra_body={},
				model="deepseek/deepseek-r1-zero:free",
				messages=history
			)

			print(completion)
			bot_reply = completion.choices[0].message.content

			print(f"Відповідь бота:\n{bot_reply}")

			json_data = await self.extract_json_from_text(bot_reply)
			
			# Зберігаємо відповідь
			cursor.execute(
				f"INSERT INTO messages_{ai_chat} (role, content, is_json) VALUES (?, ?, ?)",
				("assistant", bot_reply, int(json_data is not None))
			)
			conn.commit()

			print('create result')

			# Формуємо результат
			result = {
				"text": bot_reply,
				"has_json": json_data is not None
			}
			
			if json_data:
				result["json_data"] = json_data
			
			return result
			
		except Exception as e:
			return {"error": str(e)}
		finally:
			conn.close()
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
					await channel.send(f"```{guild.categories}```")

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
			case "ban_user":
				member_name = args[1]
				member = discord.utils.find(lambda m: m.name == member_name, guild.members)
				if member:
					await member.ban()
					await channel.send(f"Користувач {member.name} забанено на сервері!")
				else:
					await channel.send(f"Не знайдено користувача.")
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
					await channel.send(f"```{guild.text_channels}```")
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

	async def upload_scheduled_commands(self, commands_dict: dict):

		data = commands_dict

		inserted = 0
		for timestamp_str, command in data.items():
			timestamp = int(timestamp_str)
			self.cursor.execute('''
					INSERT INTO scheduled_commands (guild_id, channel_id, timestamp, command)
					VALUES (?, ?, ?, ?)
				''', (GUILD_ID, LOG_CHANNEL_ID, timestamp, command))
			inserted += 1

		self.conn.commit()

		return inserted

	@commands.has_permissions(administrator=True)
	@discord.slash_command(name="upload_json", description="Завантажити JSON файл з командами")
	async def upload_json(self, ctx: discord.ApplicationContext, file: discord.Attachment):
		if not file.filename.endswith(".json"):
			await ctx.respond("Файл має бути у форматі .json", ephemeral=True)
			return

		try:
			file_bytes = await file.read()
			data = json.loads(file_bytes.decode("utf-8"))

			inserted = await self.upload_scheduled_commands(data)

			await ctx.respond(f"Успішно додано {inserted} команд з JSON.", ephemeral=True)

		except Exception as e:
			await ctx.respond(f"Помилка при обробці файлу: {e}", ephemeral=True)

	@commands.has_permissions(administrator=True)
	@discord.slash_command(name="list_items", description="Показати всі канали та ролі на сервері")
	async def list_items(self, ctx: discord.ApplicationContext):
		guild = ctx.guild
	
		# Канали
		channel_names = [f"{channel.name} ({f'в категорії {channel.category.name}' if channel.category else ('категорія на сервері' if channel.type==discord.ChannelType.category else 'без категорії')})" for channel in guild.channels]
		channel_list = "\n - ".join(channel_names) if channel_names else "Немає каналів"
	
		# Ролі
		role_names = [role.name for role in guild.roles if role.name != "@everyone"]
		role_list = "\n - ".join(role_names) if role_names else "Немає ролей"
	
		# Змінні
		self.var_cursor.execute('SELECT name, value FROM variables WHERE guild_id = ?', (guild.id,))
		variables = self.var_cursor.fetchall()
		if variables:
			var_list = "\n - ".join(f"{name} = {value}" for name, value in variables)
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

	@discord.slash_command(name="submit_message", description="Написати ШІ повідомлення. Це може бути пропозиція, чи питання, чи ідея")
	async def submit_message(self,  ctx: discord.ApplicationContext):
		await ctx.send_modal(StrInput(self, ctx.interaction))
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
		await ctx.defer()
		await ctx.send_modal(StrInput(self, ctx.interaction))
def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(ScheduledCommands(bot))  # add the cog to the bot
