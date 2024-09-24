import json
import sys
import discord
from discord.ext import commands
import os
from cogs import account_info,collections,event_messages,radio_ua,store,without_category


radio_index = int(sys.argv[1])
intents: discord.Intents = discord.Intents.all()

with open('radio_bot_tokens.json') as file:
	radio_bot_tokens = json.loads(file.read())
	radio_name = radio_bot_tokens[radio_index][0]
	Token = radio_bot_tokens[radio_index][1]

bot = commands.Bot(intents=intents,command_prefix='....')
print(f"cogs: {os.listdir('./cogs')}")


bot.add_cog(radio_ua.RadioUa(bot, radio_name))


print(f"play {radio_name}!")

bot.run(Token)
