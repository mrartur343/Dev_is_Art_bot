import discord
from discord.ext import commands
import os

Token = "MTIyMTQwMzcwMDExNTgwMDE2NA.GPXNpX.5KvYcN1WfswDQ5Z0oJqjoT4FLUo_wMnL4uqgRs"
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(token= Token)