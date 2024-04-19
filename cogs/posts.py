import asyncio

import discord
from discord.ext import commands, pages, tasks
from modules import collections_controller

posts_channel_id = 1228087419660800040
n = '\n'


class CreateForm(discord.ui.Modal):
    def __init__(self,author, server_post: bool, *args, **kwargs) -> None:
        self.server_post = server_post
        self.author = author
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Назва", style=discord.InputTextStyle.singleline))
        self.add_item(discord.ui.InputText(label="Зміст", style=discord.InputTextStyle.paragraph))
        self.add_item(discord.ui.InputText(label="Покликання на зображення", style=discord.InputTextStyle.singleline,required=False))

    async def callback(self, interaction: discord.Interaction):
        title = self.children[0].value
        description = self.children[1].value
        url = self.children[2].value
        author = self.author
        collections_controller.post_append(f"g_{interaction.guild_id}" if self.server_post else f"{author}", title,description,url,author)
        await interaction.respond(f"Оновлення посту...", ephemeral=True)
        await update_channel(interaction.channel, interaction.guild_id)
        await interaction.respond(f"Успішно оновлено **`{title}`**!", ephemeral=True)

class EditForm(discord.ui.Modal):
    def __init__(self, title_post,desc,url,author, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Зміст", style=discord.InputTextStyle.long,value=desc))
        self.title_post =title_post
        self.url =url
        self.author = author
    async def callback(self, interaction: discord.Interaction):
        title = self.title_post
        description = self.children[0].value
        url = self.url
        author = self.author
        collections_controller.post_append(f"g_{interaction.guild_id}", title,description,url,author)
        await interaction.respond(f"Оновлення посту...", ephemeral=True)
        await update_channel(interaction.channel, interaction.guild_id)
        await interaction.respond(f"Успішно оновлено **`{title}`**!", ephemeral=True)
class PostView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View

    def __init__(self, title, desc, url, author, *args, **kwargs):
        super().__init__(*args)
        self.title=title
        self.desc=desc
        self.url=url
        self.author=author
    @discord.ui.button(style=discord.ButtonStyle.gray, emoji="📝") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        interaction: discord.Interaction
        if interaction.user.id in [int(self.author), 658217734814957578]:
            modal = EditForm(title="Змінити пост",title_post=self.title,desc=self.desc,author=self.author,url=self.url)
            await interaction.response.send_modal(modal)
        else:
            await interaction.respond("Ви не автор поста!", ephemeral=True)


class CreatePostView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View

    @discord.ui.button(label='Створити пост серверу',row=0,style=discord.ButtonStyle.green, emoji="🌌") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        interaction: discord.Interaction
        modal = CreateForm(title="Створити пост",author=interaction.user.id,server_post=True)
        await interaction.response.send_modal(modal)
    @discord.ui.button(label='Створити особистий пост',row=1,style=discord.ButtonStyle.green, emoji="🌆") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback2(self, button, interaction):
        interaction: discord.Interaction
        modal = CreateForm(title="Створити пост",author=interaction.user.id,server_post=False)
        await interaction.response.send_modal(modal)


async def get_post_embed(item, guild: bool, avatar: str = '')-> discord.Embed:
    items_embed = discord.Embed()
    items_embed.set_image(url=item["img_url"])
    items_embed.url = item["img_url"]
    items_embed.title = f"**{item['title']}**"
    items_embed.set_footer(text=item['author'])
    if guild:
        items_embed.colour = discord.Colour.purple()
    else:
        items_embed.set_thumbnail(url =avatar)
    items_embed.description = f"{item['description'].replace('&', n)}\n> - Автор: <@{item['author']}>"

    return items_embed

async def update_channel(channel: discord.TextChannel, guild_id: int):
    channel: discord.TextChannel
    history = await channel.history().flatten()
    posts_messages = {}
    msg_wait = None
    for message in history:
        if len(message.embeds) > 0:
            if message.embeds[0].title!="Створити пост":
                a_id = int(message.embeds[0].footer.text)
                posts_messages[message.embeds[0].title] = [message.embeds[0].description,message.embeds[0].url,a_id,message.id]
            else:

                create_embed = discord.Embed()
                create_embed.title = 'Оновлення постів...'
                create_embed.description = 'Зачекайте, це займе менше хвилини'
                create_embed.colour = discord.Colour.brand_red()

                await message.delete()
                msg_wait = await channel.send(embed=create_embed)
    items = collections_controller.get_posts(f"g_{guild_id}")
    for item in items:

        if not item['img_url'].split('?')[0].endswith(('.jpg', '.png', '.gif', '.jpeg')):
            item["img_url"]=''
        if not f"**{item['title']}**" in posts_messages.keys():
            items_embed =await  get_post_embed(item, True)
            await channel.send(embed=items_embed,view=PostView(title=item['title'], desc=item['description'], author=item['author'], url=item['img_url']))
        elif (posts_messages[f"**{item['title']}**"][0]!=f"{item['description'].replace('&', n)}\n> - Автор: <@{item['author']}>" or \
            posts_messages[f"**{item['title']}**"][1]!=item['img_url']) and \
                posts_messages[f"**{item['title']}**"][2]==int(item['author']):
            msg =await channel.fetch_message(posts_messages[f"**{item['title']}**"][3])
            await msg.edit(embed=await get_post_embed(item, guild=True),
                           view=PostView(timeout=None,title=item['title'], desc=item['description'], author=item['author'], url=item['img_url']))
        else:
            msg =await channel.fetch_message(posts_messages[f"**{item['title']}**"][3])
            await msg.edit(view=PostView(timeout=None,title=item['title'], desc=item['description'], author=item['author'], url=item['img_url']))


    #Оновлення учасників серверу

    async for member in channel.guild.fetch_members():
        member: discord.Member
        member_posts = collections_controller.get_posts(f"{member.id}")

        for item in member_posts:
            if not item['img_url'].split('?')[0].endswith(('.jpg', '.png', '.gif', '.jpeg')):
                item["img_url"]=''
            if not f"**{item['title']}**" in posts_messages.keys() and (member.joined_at.timestamp()-float(item['time']))<0:
                items_embed =await  get_post_embed(item, False, member.avatar.url)
                await channel.send(embed=items_embed)

    if msg_wait!=None:
        await msg_wait.delete()

    create_embed = discord.Embed()
    create_embed.title='Створити пост'
    create_embed.colour=discord.Colour.green()

    await channel.send(embed=create_embed, view=CreatePostView(timeout=None))

class Posts(commands.Cog):
    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot: discord.Bot = bot



    posts_commands = discord.SlashCommandGroup(name='post')

    @commands.Cog.listener()
    async def on_ready(self):
        print("Оновіть пости після перезапуску!")
    @posts_commands.command()
    @commands.has_permissions()
    async def update_all(self,ctx: discord.ApplicationContext):
        if ctx.author.id==658217734814957578:
            await ctx.respond(f"Оновлення...")
            await update_channel(await self.bot.fetch_channel(posts_channel_id), ctx.guild_id)
            await ctx.respond(f"Успішно оновлено всі пости!")
            print("Успіщно оновлено")
        else:
            await ctx.respond(f"Це команда тільки для розробника бота")

    @posts_commands.command()
    @commands.has_permissions()
    async def create(self,ctx: discord.ApplicationContext,
                     title: discord.Option(str),
                     description: discord.Option(str),
                     img: discord.Option(discord.Attachment, required=False)
                     ):

        collections_controller.post_append(ctx.author.id, title,description,img.url if img!=None else '',ctx.author.id)
        channel = await self.bot.fetch_channel(posts_channel_id)
        await update_channel(channel, ctx.guild.id)
        await ctx.respond(f"Успішно додано **`{title}`** до вашого акаунту!")

    @posts_commands.command()
    @commands.has_permissions()
    async def create_for_server(self,ctx: discord.ApplicationContext,
                     title: discord.Option(str),
                     description: discord.Option(str),
                     img: discord.Option(discord.Attachment, required=False)
                     ):
        await ctx.respond(f"Додаємо пост...")
        collections_controller.post_append(f"g_{ctx.guild.id}", title,description,img.url if img!=None else '', author_id=ctx.author.id)
        channel = await self.bot.fetch_channel(posts_channel_id)
        await update_channel(channel, ctx.guild.id)
        await ctx.respond(f"Успішно додано **`{title}`** до цього серверу!")

    @posts_commands.command()
    @commands.has_permissions()
    async def from_server(self,ctx: discord.ApplicationContext):
        items = collections_controller.get_posts(f"g_{ctx.guild.id}")
        if len(items) == 0:
            await ctx.respond("Поки-що жодного поста з цього серверу!")
            return
        items_pages = []
        for item in items:
            items_embed = await get_post_embed(item, True)

            items_pages.append(items_embed)

        buttons = [
            pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]

        paginator: pages.Paginator = pages.Paginator(
            pages=items_pages,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons,
        )
        await paginator.respond(ctx.interaction, ephemeral=False)


    @discord.user_command(name='Show User Posts')
    async def user_posts(self, ctx, member: discord.Member):
        items = collections_controller.get_posts(member.id)
        if len(items) == 0:
            await ctx.respond("Поки-що жодного поста від цієї людини!")
            return
        items_pages = []
        for item in items:
            items_embed =await  get_post_embed(item, False,member.avatar.url)
            items_pages.append(items_embed)

        buttons = [
            pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]

        paginator: pages.Paginator = pages.Paginator(
            pages=items_pages,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons,
        )
        await paginator.respond(ctx.interaction, ephemeral=False)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Posts(bot)) # add the cog to the bot