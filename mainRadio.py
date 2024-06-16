import discord
from discord.ext import commands
import os
from cogs import event_messages,sradio
import sys


Token = sys.argv[1]
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")


bot.add_cog(sradio.SRadio(bot))
if Token=="MTIyMTQwMzcwMDExNTgwMDE2NA.G-wjCw.gsVwNQwPKVbsELllSMGQwLy36iPeBbN-AnEEUI":
	bot.add_cog(event_messages.EventsMessages(bot))
#bot.add_cog(account_info.Account(bot))
#bot.add_cog(collections.Collections(bot))
#bot.add_cog(store.Store(bot))
#bot.add_cog(without_category.WithoutCategory(bot))

print("run radio!")

bot.run(Token)
