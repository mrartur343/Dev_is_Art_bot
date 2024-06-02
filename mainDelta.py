

import discord
from discord.ext import commands
import os
from cogs import radio_ua
TokenDelta = "MTI0Njk0MzcyOTUxMjc0MzAwNQ.G2K42w.jBuL0fvHyn0bhJFPSEEJScjQV09F2OqBHfm8-w"
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")


bot.add_cog(radio_ua.RadioUa(bot, 'Delta'))

print("run Delta bot!")

bot.run(TokenDelta)
