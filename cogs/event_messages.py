import random
import re
import typing

import discord
from discord.ext import commands



class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        supportServerButton = discord.ui.Button(label='Оцінити сервер', style=discord.ButtonStyle.gray, url='https://discord.com')
        self.add_item(supportServerButton)


class EventsMessages(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.wellcome_messages = [
                "Митець {} слова, пензля чи миші - не важливо, вітаю)",
                "Вітаю {} у нашій маленькій творчій спільноті ентузіастів!",
                "Тут місце знайдеться для кожного, вітаємо {}",
                "Не погано, що ти, {}, тут, значить тебе цікавить творчість!"
            ]


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

        guild = self.bot.get_guild(1208129686031310848)
        channel = discord.utils.get(member.guild.channels, id=1208129686572638213)
        if guild:
            print("guild ok")
        else:
            print("guild not found")

        if channel is not None:
            await channel.send(random.choice(self.wellcome_messages).format(member.mention))
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

def setup(bot):
    bot.add_cog(EventsMessages(bot))