import discord
from discord.ext import commands
from cogs import interevents, voting,server_council


Token = "MTIyMTQwMzcwMDExNTgwMDE2NA.G-wjCw.gsVwNQwPKVbsELllSMGQwLy36iPeBbN-AnEEUI"
TestToken = "MTI0MTQwMTg0NTU4NzM3ODIzNw.G_1Lg6.j_rEXnLx7lSV1-eM5VnaxfwNYPMHQ9iNhRrq3Q"

intents: discord.Intents = discord.Intents.all()

bot = commands.Bot(intents=intents,command_prefix='....')


bot.add_cog(interevents.InterEvents(bot))
bot.add_cog(voting.VoteSystem(bot))
bot.add_cog(server_council.ServerCouncil(bot))

print("run bot!")

bot.run(Token)
