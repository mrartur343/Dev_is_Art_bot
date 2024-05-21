

import discord
from discord.ext import commands
import os
from cogs import radio_ua
TokenBeta = "MTI0MTQwMTg0NTU4NzM3ODIzNw.G_Ety0.cKSf83Si70DljbTYtY6SL5gYBrFLpQYMkMWDG4"
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")


bot.add_cog(radio_ua.RadioUa(bot, 'Beta'))

print("run Alpha bot!")

bot.run(TokenBeta)
