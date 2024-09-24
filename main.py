import discord
from discord.ext import commands
from cogs import interevents


Token = "MTIyMTQwMzcwMDExNTgwMDE2NA.G-wjCw.gsVwNQwPKVbsELllSMGQwLy36iPeBbN-AnEEUI"


intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')


bot.add_cog(interevents.InterEvents(bot))

print("run Alpha radio!")

bot.run(Token)
