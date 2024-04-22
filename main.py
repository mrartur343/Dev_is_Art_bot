import asyncio

import discord
from discord.ext import commands

MainToken = 'MTIyMTQwMzcwMDExNTgwMDE2NA.GfTUcN.OeF0-yzVDBrHdV8jGOAyxn6R3IQq1q6wIqhe8g'
RadioToken = 'MTIzMTY4OTgyMjc0NjE4MTgwNg.GCOqh0.4eRa90ggrNHSns1KKCMiyX6iQoFM5a6HgjyVVg'
SocialToken = 'MTIzMjAxNDY0ODY0NDIwNjcxNA.GOABQX.79yTCCLpXlsP7JhR8iV0F3PFMgZxaX7BG5gx3A'
EconomyToken = 'MTIzMjAxMzkxOTA4NjgzNzgyMA.GqzAOv.6fqbelr8mCTrGouwAdpxA9WddCs8KtUFwRxvL0'
intents: discord.Intents = discord.Intents.all()

radio_bot = commands.Bot(intents=intents,command_prefix='....')
main_bot = commands.Bot(intents=intents,command_prefix='....')
social_bot = commands.Bot(intents=intents,command_prefix='....')
economy_bot = commands.Bot(intents=intents,command_prefix='....')

radio_cogs = ['radio_ua']
main_cogs = ['event_messages', 'without_category']
social_cogs = ['auto_posts', 'posts', 'collections']
economy_cogs = ['store']

for cog in radio_cogs:
    radio_bot.load_extension(f'cogs.{cog}')
for cog in main_cogs:
    main_bot.load_extension(f'cogs.{cog}')
for cog in social_cogs:
    social_bot.load_extension(f'cogs.{cog}')
for cog in economy_cogs:
    economy_bot.load_extension(f'cogs.{cog}')


loop = asyncio.get_event_loop()

loop.create_task(main_bot.start(MainToken))
loop.create_task(radio_bot.start(RadioToken))
loop.create_task(economy_bot.start(EconomyToken))
loop.create_task(social_bot.start(SocialToken))

loop.run_forever()