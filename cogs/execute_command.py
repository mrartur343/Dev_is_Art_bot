import discord
import logging

async def execute_command(self, guild: discord.Guild, command: str):
    args = command.split()
    if not args:
        logging.info("Пуста команда.")
        return

    def get_channel_by_id_or_name(identifier):
        try:
            ch_id = int(identifier)
            ch = guild.get_channel(ch_id)
            if ch:
                return ch
        except ValueError:
            pass
        return discord.utils.get(guild.channels, name=identifier)

    def get_category_by_id_or_name(identifier):
        try:
            cat_id = int(identifier)
            cat = discord.utils.get(guild.categories, id=cat_id)
            if cat:
                return cat
        except ValueError:
            pass
        return discord.utils.get(guild.categories, name=identifier)

    def get_role_by_id_or_name(identifier):
        try:
            role_id = int(identifier)
            role = guild.get_role(role_id)
            if role:
                return role
        except ValueError:
            pass
        return discord.utils.get(guild.roles, name=identifier)

    def get_member_by_id_or_name(identifier):
        try:
            member_id = int(identifier)
            member = guild.get_member(member_id)
            if member:
                return member
        except ValueError:
            pass
        member = discord.utils.find(lambda m: m.name == identifier or m.display_name == identifier, guild.members)
        return member

    action = args[0]
    match action:
        # --- Канали ---
        case "create_text_channel":
            name = " ".join(args[1:])
            await guild.create_text_channel(name)
            logging.info(f"Канал `{name}` створено.")

        case "create_voice_channel":
            name = " ".join(args[1:])
            await guild.create_voice_channel(name)
            logging.info(f"Канал `{name}` створено.")

        case "create_info_channel":
            name = " ".join(args[1:])
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
            }
            info_channel = await guild.create_text_channel(name, overwrites=overwrite)
            logging.info(f"ℹ️ Інформаційний канал `{name}` створено.")

        case "delete_channel":
            ch = get_channel_by_id_or_name(args[1])
            if ch:
                await ch.delete()
                logging.info(f"Канал `{ch.name}` видалено.")
            else:
                logging.info(f"Канал `{args[1]}` не знайдено.")

        case "rename_channel":
            ch = get_channel_by_id_or_name(args[1])
            new_name = " ".join(args[2:])
            if ch:
                await ch.edit(name=new_name)
                logging.info(f"Канал `{args[1]}` перейменовано на `{new_name}`.")
            else:
                logging.info(f"Канал `{args[1]}` не знайдено.")

        case "set_channel_topic":
            ch = get_channel_by_id_or_name(args[1])
            topic = " ".join(args[2:])
            if ch and isinstance(ch, discord.TextChannel):
                await ch.edit(topic=topic)
                logging.info(f"Тема каналу `{args[1]}` оновлена.")
            else:
                logging.info(f"Канал `{args[1]}` не знайдено або він не текстовий.")

        case "create_category":
            name = " ".join(args[1:])
            await guild.create_category(name)
            logging.info(f"📁 Категорію `{name}` створено.")

        case "move_channel":
            ch = get_channel_by_id_or_name(args[1])
            category = get_category_by_id_or_name(args[2])
            if ch and category:
                await ch.edit(category=category)
                logging.info(f"📂 Канал `{args[1]}` переміщено до категорії `{args[2]}`.")
            else:
                logging.info("❌ Канал або категорію не знайдено.")

        # --- Ролі ---
        case "create_role":
            name = " ".join(args[1:])
            await guild.create_role(name=name)
            logging.info(f"Роль `{name}` створено.")

        case "delete_role":
            role = get_role_by_id_or_name(args[1])
            if role:
                await role.delete()
                logging.info(f"Роль `{args[1]}` видалено.")
            else:
                logging.info(f"Роль `{args[1]}` не знайдено.")

        case "rename_role":
            role = get_role_by_id_or_name(args[1])
            new_name = " ".join(args[2:])
            if role:
                await role.edit(name=new_name)
                logging.info(f"Роль `{args[1]}` перейменовано на `{new_name}`.")
            else:
                logging.info(f"Роль `{args[1]}` не знайдено.")

        # --- Користувачі / ролі ---
        case "add_role":
            member = get_member_by_id_or_name(args[1])
            role = get_role_by_id_or_name(args[2])
            if member and role:
                await member.add_roles(role)
                logging.info(f"Роль `{args[2]}` додано користувачу `{args[1]}`.")
            else:
                logging.info(f"Не знайдено користувача або ролі.")

        case "remove_role":
            member = get_member_by_id_or_name(args[1])
            role = get_role_by_id_or_name(args[2])
            if member and role:
                await member.remove_roles(role)
                logging.info(f"Роль `{args[2]}` видалено в користувача `{args[1]}`.")
            else:
                logging.info(f"Не знайдено користувача або ролі.")

        case "ban_user":
            member = get_member_by_id_or_name(args[1])
            if member:
                await member.ban()
                logging.info(f"Користувач `{args[1]}` забанено на сервері!")
            else:
                logging.info(f"Не знайдено користувача.")

        case "dm_user":
            member = get_member_by_id_or_name(args[1])
            msg = " ".join(args[2:])
            if member:
                try:
                    await member.send(msg)
                    logging.info(f"📨 Повідомлення надіслано користувачу `{args[1]}`.")
                except discord.Forbidden:
                    logging.info("❌ Не вдалося надіслати повідомлення. Можливо, користувач вимкнув DM.")
            else:
                logging.info(f"❌ Користувача `{args[1]}` не знайдено.")

        # --- Повідомлення ---
        case "send_message":
            if len(args) < 3:
                logging.info("❌ Використання: send_message idКаналу Повідомлення")
                return

            target_channel = get_channel_by_id_or_name(args[1])
            raw_message = " ".join(args[2:])
            if not target_channel:
                logging.info(f"❌ Канал `{args[1]}` не знайдено.")
                return

            self.var_cursor.execute("SELECT name, value FROM variables WHERE guild_id = ?", (guild.id,))
            variables = dict(self.var_cursor.fetchall())
            for key, value in variables.items():
                raw_message = raw_message.replace(f"{{{key}}}", value)

            await target_channel.send(raw_message)
            logging.info(f"✅ Повідомлення надіслано до каналу `{args[1]}`.")

        # --- Сервер ---
        case "change_server_name":
            new_name = " ".join(args[1:])
            await guild.edit(name=new_name)
            logging.info(f"Назву сервера змінено на `{new_name}`.")

        case "set_variable":
            if len(args) < 3:
                logging.info("❌ Формат: `set_variable назва значення`")
                return

            var_name = args[1]
            var_value = " ".join(args[2:])
            self.var_cursor.execute('''
                INSERT INTO variables (guild_id, name, value)
                VALUES (?, ?, ?)
                ON CONFLICT(guild_id, name) DO UPDATE SET value = excluded.value
            ''', (guild.id, var_name, var_value))
            self.var_db.commit()
            logging.info(f"✅ Змінну `{var_name}` встановлено на `{var_value}`.")

        # --- HR завдання ---
        case "hr_assign_role":
            # Формат: hr_assign_role user role
            if len(args) < 3:
                logging.info("❌ Формат: hr_assign_role користувач роль")
                return

            user_identifier = args[1]
            role_identifier = args[2]
            member = get_member_by_id_or_name(user_identifier)
            role = get_role_by_id_or_name(role_identifier)

            if not member:
                logging.info(f"❌ Користувача `{user_identifier}` не знайдено.")
                return
            if not role:
                logging.info(f"❌ Роль `{role_identifier}` не знайдено.")
                return

            # Отримати картку учасника
            card = await self.get_user_card(member.id) if hasattr(self, "get_user_card") else None
            card_text = f"Картка учасника:\n{card}\n\n" if card else "Картка учасника не знайдена.\n\n"

            # Формуємо запит для HR ШІ
            hr_prompt = (
                f"Користувач: {member.display_name} (ID: {member.id})\n"
                f"Роль: {role.name} (ID: {role.id})\n"
                f"{card_text}"
                f"Відповідь має містити JSON із завданням для бота по додаванню ролі користувачу."
            )

            # Відправляємо запит до HR ШІ
            if hasattr(self, "chat_with_deepseek"):
                hr_result = await self.chat_with_deepseek(hr_prompt, 'hr')
                logging.info(f"[hr_assign_role] Відповідь HR ШІ: {hr_result}")

                # Якщо відповідь містить json_data із завданнями, завантажуємо їх як у admin
                if isinstance(hr_result, dict) and "json_data" in hr_result:
                    if hasattr(self, "upload_scheduled_commands"):
                        await self.upload_scheduled_commands(hr_result["json_data"])
                        logging.info("[hr_assign_role] Завдання HR ШІ додано до scheduled_commands.")
                    else:
                        logging.info("[hr_assign_role] Не знайдено метод upload_scheduled_commands.")
                else:
                    logging.info("[hr_assign_role] Відповідь HR ШІ не містить json_data.")
            else:
                logging.info("[hr_assign_role] Не знайдено метод chat_with_deepseek.")

        case _:
            logging.info(f"Невідома команда: `{command}`")