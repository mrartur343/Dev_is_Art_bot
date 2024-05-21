

import discord
from discord.ext import commands
import os
from cogs import radio_ua
TokenGamma = "MTI0MTQwMjM4MTAzMjM1ODEyMA.GY8aZi.G5ahHzdu0gJH_dSU9e3cTFjDQvlBYTaQlf-Z90"
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")


bot.add_cog(radio_ua.RadioUa(bot, 'Gamma'))

print("run Alpha bot!")

bot.run(TokenGamma)
