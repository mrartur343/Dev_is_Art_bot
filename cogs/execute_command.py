import discord

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
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
            }
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
            member = discord.utils.find(lambda m: m.name == target_name or m.display_name == target_name, guild.members)
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
            target_channel = discord.utils.get(guild.text_channels, name=target_channel_name)
            if not target_channel:
                await channel.send(f"❌ Канал `{target_channel_name}` не знайдено.")
                await channel.send(f"```{guild.text_channels}```")
                return

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