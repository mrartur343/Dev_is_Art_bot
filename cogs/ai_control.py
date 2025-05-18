import json
import os
import random
import sqlite3
import time
from openai import OpenAI
import logging
import io

import discord
from discord import InputTextStyle
from discord.ext import commands, tasks
from discord.ui import InputText
from .db_config import DB_NAME, SCHEDULED_DB, VARIABLES_DB, CARDS_DB
from .execute_command import execute_command

AI_LIST = ['getter', 'owner', 'admin', 'eventer', 'moderator', 'designer', 'hr']
FIRST_MESSAGE_FILE = 'first_messages/{ai_name}.txt'
MODERATOR_RULES_FILE = "moderator_rules.json"  # Додаємо шлях до файлу
API_KEY = os.environ.get('AI_Token')
API_URL = "https://openrouter.ai/api/v1"

# --- Додаємо цю секцію ---
DB_FOLDER = "db"
os.makedirs(DB_FOLDER, exist_ok=True)
DB_NAME = os.path.join(DB_FOLDER, "chat_history.db")
SCHEDULED_DB = os.path.join(DB_FOLDER, "scheduled_commands.db")
VARIABLES_DB = os.path.join(DB_FOLDER, "variables.db")
# -------------------------

LOG_CHANNEL_ID = 1371537439495028856
GUILD_ID = 1371121463717003344

LOG_FILE = "bot_commands.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    encoding="utf-8"
)

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
        await interaction.respond("✅ Повідомлення надіслано!", ephemeral=True)

        await self.cog.send_submit_to_ai(msg, author_nickname=interaction.user.global_name)


class ScheduledCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.conn = sqlite3.connect(SCHEDULED_DB)
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

        self.var_db = sqlite3.connect(VARIABLES_DB)
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

        # --- Створення таблиць для всіх AI з AI_LIST ---
        for ai_name in AI_LIST:
            self.api_cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS messages_{ai_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_json BOOLEAN DEFAULT 0
                )
            ''')
        # -----------------------------------------------

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
        self.moderator_check_limit=35
        self.moderator_check_count=35

        self.check_scheduled_commands.start()
        self.append_scheduled_commands.start()

        self.message_per_day = 0

        # --- Таблиця карток учасників ---
        self.cards_db = sqlite3.connect(CARDS_DB)
        self.cards_cursor = self.cards_db.cursor()
        self.cards_cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cards (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                card_content TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cards_db.commit()

        # --- Завантаження правил модератора з файлу ---
        self.moderator_rules = None
        if os.path.exists(MODERATOR_RULES_FILE):
            try:
                with open(MODERATOR_RULES_FILE, "r", encoding="utf-8") as f:
                    self.moderator_rules = json.load(f)
            except Exception as e:
                print(f"Не вдалося завантажити правила модератора: {e}")
        # ----------------------------------------------

    def cog_unload(self):
        self.check_scheduled_commands.cancel()
        self.conn.close()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if not msg.author.bot:
            self.message_per_day += 1

            random_k = random.random()

            msg_k = 1-(1 / (2 + (self.moderator_check_count ** 1.5)))

            print(f"{random_k} | {msg_k}")

            if random_k < msg_k:
                await msg.add_reaction("🤖")
                await self.send_message_to_moderator(msg.content, msg.author.global_name, msg.author.id)

    async def send_message_to_moderator(self, submit_text, author_nickname, author_id=None):
        # Отримати картку учасника
        card = await self.get_user_card(author_id) if author_id else None
        card_text = f"Картка учасника:\n{card}\n\n" if card else ""
        user_id_text = f"ID користувача: {author_id}\n" if author_id else ""
        moderator_result = await self.chat_with_deepseek(
            f'{user_id_text}{card_text}Інструкція: {self.moderator_rules}\n'
            f'Зараз: {int(time.time())}\n'
            f'Автор: {author_nickname}\n'
            f'Повідомлення: {submit_text}', 'moderator'
        )

        await self.save_user_card(author_id, author_nickname, moderator_result['text'].split('```')[0]) if author_id else None

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

        self.moderator_check_count=self.moderator_check_limit

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
        guild = self.bot.get_guild(GUILD_ID)
        # Формуємо списки id - назва для каналах, ролях, користувачах, категоріях
        if guild:
            channels_text = "\n".join([f"{ch.id} - {ch.name}" for ch in guild.channels])
            roles_text = "\n".join([f"{role.id} - {role.name}" for role in guild.roles])
            members_text = "\n".join([f"{member.id} - {member.display_name}" for member in guild.members])
            categories_text = "\n".join([f"{cat.id} - {cat.name}" for cat in guild.categories])
        else:
            channels_text = roles_text = members_text = categories_text = ""

        if 'moderator' in json_data:
            try:
                self.moderator_rules = json_data['moderator']
                # --- Зберігаємо правила модератора у файл ---
                try:
                    with open(MODERATOR_RULES_FILE, "w", encoding="utf-8") as f:
                        json.dump(self.moderator_rules, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Не вдалося зберегти правила модератора: {e}")
                # ---------------------------------------------
            except Exception as e:
                print(e)
        if 'admin' in json_data:
            try:
                admin_prompt = (
                    json_data["admin"]
                    + f'\n\nКанали:\n{channels_text}\n\nКатегорії:\n{categories_text}\n\nРолі:\n{roles_text}\n\nКористувачі:\n{members_text}'
                    + f'\n \n \n timestamp зараз - {int(time.time())}'
                )
                admin_result = await self.chat_with_deepseek(admin_prompt, 'admin')
                await self.upload_scheduled_commands(admin_result['json_data'])
            except Exception as e:
                print(e)

        if 'eventer' in json_data:
            try:
                eventer_prompt = (
                    json_data["eventer"]
                    + f'\n\nКанали:\n{channels_text}\n\nКатегорії:\n{categories_text}\n\nРолі:\n{roles_text}\n\nКористувачі:\n{members_text}'
                    + f'\n \n \n timestamp зараз - {int(time.time())}'
                )
                eventer_result = await self.chat_with_deepseek(eventer_prompt, 'eventer')
                await self.upload_scheduled_commands(eventer_result['json_data'])
            except Exception as e:
                print(e)

        if 'designer' in json_data:
            try:
                designer_prompt = (
                    json_data["designer"]
                    + f'\n\nКанали:\n{channels_text}\n\nКатегорії:\n{categories_text}\n\nРолі:\n{roles_text}\n\nКористувачі:\n{members_text}'
                    + f'\n \n \n timestamp зараз - {int(time.time())}'
                )
                designer_result = await self.chat_with_deepseek(designer_prompt, 'designer')
                await self.upload_scheduled_commands(designer_result['json_data'])
            except Exception as e:
                print(e)

    @tasks.loop(seconds=10)
    async def check_scheduled_commands(self):
        now = int(time.time())
        self.cursor.execute('SELECT id, guild_id, channel_id, command FROM scheduled_commands WHERE timestamp <= ?', (now,))
        rows = self.cursor.fetchall()

        for row in rows:
            cmd_id, guild_id, channel_id, command = row
            guild = self.bot.get_guild(GUILD_ID)
            try:
                await execute_command(self, guild, command)  # Виклик з окремого файлу
            except Exception as e:
                print(f"Помилка при виконанні `{command}`: {e}")
            self.cursor.execute('DELETE FROM scheduled_commands WHERE id = ?', (cmd_id,))
            self.conn.commit()

    async def extract_json_from_text(self, text):
        """Спробує знайти та розпарсити JSON у тексті відповіді"""

        print("try to find json:\n "+text+"\n\n\n")
        try:
            # Шукаємо початок JSON (можливі варіанти)
            if '```' in text:
                json_str = text.split('```json' if '```json' in text else '```')[1].split('```')[0]
            elif '{{' in text and '}}' in text:
                json_str = '{'+text.split('{{')[1].split('}}')[0] + '}'
            else:
                json_str = '{'+text.split('{\n{\n')[1].split('\n}\n}')[0] + '}'

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
                    "content": "Будь ласка, поверни відповідь у форматі JSON. Дані мають бути валідним JSON у межах текстової відповіді. json відповідь мають бути всередині ```{...}``` де {...} це json відповідь"
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
        self.cursor.execute('''
            SELECT timestamp, command, channel_id FROM scheduled_commands
            WHERE guild_id = ?
            ORDER BY timestamp ASC
        ''', (ctx.guild.id,))
        rows = self.cursor.fetchall()

        if not rows:
            log_msg = f"[view_scheduled] 🔍 Немає запланованих завдань для гільдії {ctx.guild.id}"
            logging.info(log_msg)
            await ctx.respond("🔍 Немає запланованих завдань.", ephemeral=True)
            return

        # Формуємо JSON-структуру для експорту
        tasks_json = {
            str(ts): {
                "command": cmd,
                "channel_id": ch_id
            }
            for ts, cmd, ch_id in rows
        }

        # Створюємо файл у пам'яті
        json_bytes = json.dumps(tasks_json, ensure_ascii=False, indent=2).encode("utf-8")
        file = discord.File(io.BytesIO(json_bytes), filename="scheduled_tasks.json")

        await ctx.respond(
            content="📅 Ось ваші заплановані завдання у форматі JSON:",
            file=file,
            ephemeral=True
        )

        log_msg = f"[view_scheduled] 📅 Заплановані завдання для гільдії {ctx.guild.id}:\n" + "\n".join(
            [f"• ⏰ <t:{ts}:F> в <#{ch_id}> — `{cmd}`" for ts, cmd, ch_id in rows]
        )
        logging.info(log_msg)

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
        await ctx.send_modal(StrInput(self, ctx.interaction))

    async def get_user_card(self, user_id: int):
        self.cards_cursor.execute('SELECT card_content FROM user_cards WHERE user_id = ?', (user_id,))
        row = self.cards_cursor.fetchone()
        return row[0] if row else None

    async def chat_with_deepseek_text(self, user_message, ai_chat: str, system_prompt=None):
        """
        Отримати відповідь від Deepseek без очікування JSON, тільки текст.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"INSERT INTO messages_{ai_chat} (role, content) VALUES (?, ?)",
                ("user", user_message)
            )
            conn.commit()

            cursor.execute(f"SELECT role, content FROM messages_{ai_chat} ORDER BY timestamp")
            history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

            if system_prompt:
                history.insert(0, {"role": "system", "content": system_prompt})

            completion = client.chat.completions.create(
                extra_body={},
                model="deepseek/deepseek-r1-zero:free",
                messages=history
            )

            bot_reply = completion.choices[0].message.content

            cursor.execute(
                f"INSERT INTO messages_{ai_chat} (role, content, is_json) VALUES (?, ?, ?)",
                ("assistant", bot_reply, 0)
            )
            conn.commit()

            return bot_reply

        except Exception as e:
            return f"Помилка: {e}"
        finally:
            conn.close()

    @commands.has_permissions(administrator=True)
    @discord.slash_command(name="set_user_card", description="Задати або оновити картку учасника")
    async def set_user_card(self, ctx: discord.ApplicationContext, member: discord.Member, *, card: str):
        await self.save_user_card(member.id, member.display_name, card)
        await ctx.respond(f"Картку для {member.display_name} оновлено.", ephemeral=True)

    async def save_user_card(self, user_id: int, username: str, card_content: str):
        self.cards_cursor.execute('''
            INSERT INTO user_cards (user_id, username, card_content, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                card_content=excluded.card_content,
                updated_at=CURRENT_TIMESTAMP
        ''', (user_id, username, card_content))
        self.cards_db.commit()

    @discord.slash_command(name="view_user_card", description="Переглянути картку учасника")
    async def view_user_card(self, ctx: discord.ApplicationContext, member: discord.Member):
        """Показати картку учасника за його Discord-аккаунтом"""
        card = await self.get_user_card(member.id)
        if card:
            logging.info(f"[view_user_card] Картка для {member.display_name} (ID: {member.id}):\n{card}")
            embed = discord.Embed(
                title=f"Картка учасника: {member.display_name}",
                description=card,
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            logging.info(f"[view_user_card] Картка для {member.display_name} (ID: {member.id}) не знайдена.")
            await ctx.respond(f"Картка для {member.display_name} не знайдена.", ephemeral=True)

def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(ScheduledCommands(bot))  # add the cog to the bot
