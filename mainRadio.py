import discord
from discord.ext import commands
import os
from cogs import event_messages,sradio
import sys


if sys.argv[1]=='a':
	radio_index = 0
	Token = "MTIyMTQwMzcwMDExNTgwMDE2NA.G-wjCw.gsVwNQwPKVbsELllSMGQwLy36iPeBbN-AnEEUI"
else:
	radio_index = 1
	Token = 'MTI0MTQwMTg0NTU4NzM3ODIzNw.GnPixU.USNyu1X811MNAKgw06ZOBVwutH5bgOfunbjl9I'
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")

if sys.argv[1]=='a':
	bot.add_cog(event_messages.EventsMessages(bot))

bot.add_cog(sradio.SRadio(bot,radio_index))

#bot.add_cog(account_info.Account(bot))
#bot.add_cog(collections.Collections(bot))
#bot.add_cog(store.Store(bot))
#bot.add_cog(without_category.WithoutCategory(bot))

print("run Alpha radio!")

bot.run(Token)
