import os
import discord
from discord.ext import commands
from cogs import ai_control
from dotenv import load_dotenv
load_dotenv()


Token = os.environ.get("Token")

intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')


bot.add_cog(ai_control.ScheduledCommands(bot))

print("run bot!")

bot.run(Token)
