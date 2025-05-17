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
            try:
                ch_id = int(args[1])
                ch = guild.get_channel(ch_id)
            except:
                ch = None
            if ch:
                await ch.delete()
                await channel.send(f"Канал з id `{args[1]}` видалено.")
            else:
                await channel.send(f"Канал з id `{args[1]}` не знайдено.")

        case "rename_channel":
            try:
                ch_id = int(args[1])
                new_name = " ".join(args[2:])
                ch = guild.get_channel(ch_id)
            except:
                ch = None
            if ch:
                await ch.edit(name=new_name)
                await channel.send(f"Канал з id `{args[1]}` перейменовано на `{new_name}`.")
            else:
                await channel.send(f"Канал з id `{args[1]}` не знайдено.")

        case "set_channel_topic":
            try:
                ch_id = int(args[1])
                topic = " ".join(args[2:])
                ch = guild.get_channel(ch_id)
            except:
                ch = None
            if ch and isinstance(ch, discord.TextChannel):
                await ch.edit(topic=topic)
                await channel.send(f"Тема каналу з id `{args[1]}` оновлена.")
            else:
                await channel.send(f"Канал з id `{args[1]}` не знайдено або він не текстовий.")

        case "create_category":
            name = " ".join(args[1:])
            await guild.create_category(name)
            await channel.send(f"📁 Категорію `{name}` створено.")

        case "move_channel":
            try:
                ch_id = int(args[1])
                cat_id = int(args[2])
                ch = guild.get_channel(ch_id)
                category = discord.utils.get(guild.categories, id=cat_id)
            except:
                ch = None
                category = None
            if ch and category:
                await ch.edit(category=category)
                await channel.send(f"📂 Канал з id `{args[1]}` переміщено до категорії з id `{args[2]}`.")
            else:
                await channel.send("❌ Канал або категорію не знайдено.")

        # --- Ролі ---
        case "create_role":
            name = " ".join(args[1:])
            await guild.create_role(name=name)
            await channel.send(f"Роль `{name}` створено.")

        case "delete_role":
            try:
                role_id = int(args[1])
                role = guild.get_role(role_id)
            except:
                role = None
            if role:
                await role.delete()
                await channel.send(f"Роль з id `{args[1]}` видалено.")
            else:
                await channel.send(f"Роль з id `{args[1]}` не знайдено.")

        case "rename_role":
            try:
                role_id = int(args[1])
                new_name = " ".join(args[2:])
                role = guild.get_role(role_id)
            except:
                role = None
            if role:
                await role.edit(name=new_name)
                await channel.send(f"Роль з id `{args[1]}` перейменовано на `{new_name}`.")
            else:
                await channel.send(f"Роль з id `{args[1]}` не знайдено.")

        # --- Користувачі / ролі ---
        case "add_role":
            try:
                member_id = int(args[1])
                role_id = int(args[2])
                member = guild.get_member(member_id)
                role = guild.get_role(role_id)
            except:
                member = None
                role = None
            if member and role:
                await member.add_roles(role)
                await channel.send(f"Роль з id `{args[2]}` додано користувачу з id `{args[1]}`.")
            else:
                await channel.send(f"Не знайдено користувача або ролі.")

        case "remove_role":
            try:
                member_id = int(args[1])
                role_id = int(args[2])
                member = guild.get_member(member_id)
                role = guild.get_role(role_id)
            except:
                member = None
                role = None
            if member and role:
                await member.remove_roles(role)
                await channel.send(f"Роль з id `{args[2]}` видалено в користувача з id `{args[1]}`.")
            else:
                await channel.send(f"Не знайдено користувача або ролі.")

        case "ban_user":
            try:
                member_id = int(args[1])
                member = guild.get_member(member_id)
            except:
                member = None
            if member:
                await member.ban()
                await channel.send(f"Користувач з id `{args[1]}` забанено на сервері!")
            else:
                await channel.send(f"Не знайдено користувача.")

        case "dm_user":
            try:
                member_id = int(args[1])
                msg = " ".join(args[2:])
                member = guild.get_member(member_id)
            except:
                member = None
                msg = ""
            if member:
                try:
                    await member.send(msg)
                    await channel.send(f"📨 Повідомлення надіслано користувачу з id `{args[1]}`.")
                except discord.Forbidden:
                    await channel.send("❌ Не вдалося надіслати повідомлення. Можливо, користувач вимкнув DM.")
            else:
                await channel.send(f"❌ Користувача з id `{args[1]}` не знайдено.")

        # --- Повідомлення ---
        case "send_message":
            if len(args) < 3:
                await channel.send("❌ Використання: send_message idКаналу Повідомлення")
                return

            try:
                target_channel_id = int(args[1])
                raw_message = " ".join(args[2:])
                target_channel = guild.get_channel(target_channel_id)
            except:
                target_channel = None
                raw_message = ""
            if not target_channel:
                await channel.send(f"❌ Канал з id `{args[1]}` не знайдено.")
                return

            self.var_cursor.execute("SELECT name, value FROM variables WHERE guild_id = ?", (guild.id,))
            variables = dict(self.var_cursor.fetchall())
            for key, value in variables.items():
                raw_message = raw_message.replace(f"{{{key}}}", value)

            await target_channel.send(raw_message)
            await channel.send(f"✅ Повідомлення надіслано до каналу з id `{args[1]}`.")

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