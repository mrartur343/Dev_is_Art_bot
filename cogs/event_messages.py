import re
import typing

import discord
from discord.ext import commands
import pillow



class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        supportServerButton = discord.ui.Button(label='Оцінити сервер', style=discord.ButtonStyle.gray, url='https://discord.com')
        self.add_item(supportServerButton)


class EventsMessages(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.auto_roles_id = [
            1208129686039826506,
            1208129686052278326,
            1208129686077706326,
            1208129686090285132,
            1229053233201283136
        ]



    @commands.Cog.listener()
    async def on_ready(self):
        print("Welcome: ON")


        guild = self.bot.get_guild(1208129686031310848)

        auto_roles: typing.List[discord.Role] = []
        for id in self.auto_roles_id:
            auto_roles.append(await guild._fetch_role(id))

        members = await guild.fetch_members().flatten()



        for member in members:
            try:
                member_roles = member.roles
                for role in auto_roles:
                    if not role in member_roles:
                        await member.add_roles(role)
            except:
                print(f"error: {member.name}")
        print("Autoroles: ADD")



    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # noinspection PyTypeChecker
        pillow.get_wellcome(f"Wellcome, @{member.name}")

        guild = self.bot.get_guild(1208129686031310848)
        channel = discord.utils.get(member.guild.channels, id=1208129686127911027)
        if guild:
            print("guild ok")
        else:
            print("guild not found")

        if channel is not None:
            await channel.send(f":inbox_tray: | {member.mention} ({member.name}) ({member.id})", file=discord.File('media/wellcome.png'))
        else:
            print("id channel wrong")

        #autoroles

        auto_roles: typing.List[discord.Role] = []
        for id in self.auto_roles_id:
            auto_roles.append(await guild._fetch_role(id))

        members = await guild.fetch_members().flatten()

        for member in members:
            for role in auto_roles:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, payload: discord.Member):
        user: discord.Member = payload
        # noinspection PyTypeChecker
        pillow.get_wellcome(f"Wellcome, @{user.name}")

        guild = self.bot.get_guild(1208129686031310848)
        channel = discord.utils.get(guild.channels, id=1208129686127911027)
        if guild:
            print("guild ok")
        else:
            print("guild not found")

        if channel is not None:
            await channel.send(f":outbox_tray: | @{user.name} ({user.id})")
        else:
            print("id channel wrong")

    @commands.Cog.listener()
    async def on_member_ban(self,guild, member: discord.User):
        # noinspection PyTypeChecker

        guild = self.bot.get_guild(1208129686031310848)
        channel = discord.utils.get(guild.channels, id=1208129686127911027)
        if guild:
            print("guild ok")
        else:
            print("guild not found")

        if channel is not None:
            await channel.send(f"🔨 | {member.name} ({member.id}) був забанений")
        else:
            print("id channel wrong")


    @commands.Cog.listener()
    async def on_member_unban(self,guild, member: discord.User):
        # noinspection PyTypeChecker

        guild = self.bot.get_guild(1208129686031310848)
        channel = discord.utils.get(guild.channels, id=1208129686127911027)
        if guild:
            print("guild ok")
        else:
            print("guild not found")

        if channel is not None:
            await channel.send(f"🕊️ | {member.name} ({member.id}) був розбанений")
        else:
            print("id channel wrong")
def setup(bot):
    bot.add_cog(EventsMessages(bot))