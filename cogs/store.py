import discord
from discord.ext import commands
from modules import store_controller

class StoreSelect(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Магазин кольорів", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Vanilla",
                description="Pick this if you like vanilla!"
            ),
            discord.SelectOption(
                label="Chocolate",
                description="Pick this if you like chocolate!"
            ),
            discord.SelectOption(
                label="Strawberry",
                description="Pick this if you like strawberry!"
            )
        ]
    )
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")

class Store(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @discord.slash_command() # we can also add application commands
    async def store(self, ctx):
        await ctx.respond('Goodbye!')

    @discord.user_command()
    async def greet(self, ctx, member: discord.Member):
        await ctx.respond(f'{ctx.author.mention} says hello to {member.mention}!')

    @commands.Cog.listener() # we can add event listeners to our cog
    async def on_member_join(self, member): # this is called when a member joins the server
    # you must enable the proper intents
    # to access this event.
    # See the Popular-Topics/Intents page for more info
        await member.send('Welcome to the server!')

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Store(bot)) # add the cog to the bot