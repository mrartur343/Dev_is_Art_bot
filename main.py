import os
import discord
from discord.ext import commands
from cogs import voting,server_council


Token = os.environ.get("Token")

intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')


bot.add_cog(voting.VoteSystem(bot))
bot.add_cog(server_council.ServerCouncil(bot))

print("run bot!")

bot.run(Token)
