import discord
from discord.ext import commands
import os
from cogs import account_info,collections,event_messages,radio_ua,store,without_category

Token = "MTIyMTQwMzcwMDExNTgwMDE2NA.G-wjCw.gsVwNQwPKVbsELllSMGQwLy36iPeBbN-AnEEUI"
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")


bot.add_cog(radio_ua.RadioUa(bot, 'Alpha'))
#bot.add_cog(account_info.Account(bot))
#bot.add_cog(collections.Collections(bot))
#bot.add_cog(event_messages.EventsMessages(bot))
#bot.add_cog(store.Store(bot))
#bot.add_cog(without_category.WithoutCategory(bot))

print("run Alpha radio!")

bot.run(Token)