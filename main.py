import discord
from discord.ext import commands
import os
import asyncio
from cogs import account_info,collections,event_messages,radio_ua,store,without_category
Token = "MTIyMTQwMzcwMDExNTgwMDE2NA.GPXNpX.5KvYcN1WfswDQ5Z0oJqjoT4FLUo_wMnL4uqgRs"


TokenBeta = "MTI0MTQwMTg0NTU4NzM3ODIzNw.GdmYNv.5a_FWy0YMO595ZKURWYcyluyMAZS7eH-4nUG4g"
TokenGamma = "MTI0MTQwMjM4MTAzMjM1ODEyMA.GY8aZi.G5ahHzdu0gJH_dSU9e3cTFjDQvlBYTaQlf-Z90"


RadioToken = "MTIzNjY4MjE2NTQyMTYwNDg3Ng.GXZrPZ.GFBtPubu6l-JlkkiX7etWheX82wfETFODJpSHA"
intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')
bot_b = commands.Bot(intents=intents,command_prefix='....')
bot_g = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")


bot.add_cog(account_info.Account(bot))
bot.add_cog(collections.Collections(bot))
bot.add_cog(event_messages.EventsMessages(bot))
bot.add_cog(radio_ua.RadioUa(bot, 'Alpha'))
bot.add_cog(store.Store(bot))
bot.add_cog(without_category.WithoutCategory(bot))


bot_b.add_cog(radio_ua.RadioUa(bot_b, 'Beta'))
bot_g.add_cog(radio_ua.RadioUa(bot_g, 'Gamma'))

print("run bot!")

asyncio.run(bot.start(Token))
asyncio.run(bot_b.start(TokenBeta))
asyncio.run(bot_g.start(TokenGamma))



