import asyncio
import datetime
import json
import os.path
from os import listdir
from typing import Dict, Tuple, List, Type, Any
import server_request_inputs
import discord
from discord.ext import commands, pages

actions: List[Tuple[discord.Embed, Type[object]]] = [
	(discord.Embed(title="Власна пропозиція",
	               fields=[discord.EmbedField(name='name', value=''), discord.EmbedField(name='comment', value='')])
	 , server_request_inputs.OwnRequest),
]



council_role_id = 1249713455787671583



class VoteView(discord.ui.View):
	def __init__(self, request_name, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.request_name = request_name

	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="Ваш голос:",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		max_values=1,  # the maximum number of values that can be selected by the users
		options=[  # the list of options from which users can choose, a required field
			discord.SelectOption(
				label="Підтримати",
				description="Проголосувати за пропозицію",
				value='1',
				emoji='✅'
			),
			discord.SelectOption(
				label="Не підтримати",
				description="Проголосувати проти пропозиції",
				value='2',
				emoji='⛔'
			),
			discord.SelectOption(
				label="Утриматись",
				description="Не голосувати. Значення за замовчуванням",
				value='3',
				emoji='😴'
			)
		]
	)
	async def select_callback(self, select: discord.ui.Select,
	                          interaction: discord.Interaction):  # the function called when the user is done selecting options
		with open(f'server_requests/{self.request_name}.json', 'r') as file:
			request_info = json.loads(file.read())

		s = int(select.values[0])

		if str(interaction.user.id) in request_info['voting'].keys():
			request_info['voting'][str(interaction.user.id)] = s

			with open(f'server_requests/{self.request_name}.json', 'w') as file:
				json.dump(request_info, file)

			await interaction.respond(f"Ваш вибір {'погодитись' if s==1 else ('не погодитись' if s==2 else 'утриматись')} буде враховано!", ephemeral= True)

		else:
			await interaction.respond(f"Вас немає у раді серверу!", ephemeral= True)




class RequestView(discord.ui.View):
	def __init__(self,server_council_ids, *args, **kwargs):
		self.server_council_ids=server_council_ids
		super().__init__(timeout=None, *args)
	@discord.ui.select(  # the decorator that lets you specify the properties of the select menu
		placeholder="Виберіть тип пропозиції",  # the placeholder text that will be displayed if nothing is selected
		min_values=1,  # the minimum number of values that must be selected by the users
		max_values=1,  # the maximum number of values that can be selected by the users
		options=[  # the list of options from which users can choose, a required field
			discord.SelectOption(
				label="Текстова ідея",
				description="Напиши що на твою думку повинна зробити рада!",
				value='0',
				emoji='💡'
			),
			discord.SelectOption(
				label="Демократія (скоро)",
				description="Дострокові вибори, переобрання міністрів, тощо",
				value='1',
				emoji='🪧'
			),
			discord.SelectOption(
				label="Ролі й посади (скоро)",
				description="Додати або забрати роль у людини",
				value='2',
				emoji='🚩'
			)
		]
	)
	async def select_callback(self, select: discord.ui.Select,
	                          interaction: discord.Interaction):  # the function called when the user is done selecting options

		if select.values[0] in ["1","2"]:
			await interaction.respond("Ці види пропозицій будуть додані вже скоро!",ephemeral=True)


		action = actions[int(select.values[0])]



		await interaction.respond(embed=action[0],view=action[1](self.server_council_ids, interaction.user.id))


class ServerCouncil(commands.Cog):

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@commands.Cog.listener()
	async def on_message(self,msg:discord.Message):
		print(msg.reference.to_dict())
		if (msg.author.id == 767783132031352884 and msg.channel.id == 1227710915072495740 and msg.thread is None):
			await msg.delete()
			await msg.author.send("Рада серверу Dev is Art заборонила вам писати в новини, твоє повідомлення видалене")
	@commands.Cog.listener()
	async def on_ready(self):
		council_channel = self.bot.get_channel(1247198900775944202)


		council_messages = await council_channel.history(limit=1000).flatten()
		for message in council_messages:
			try:
				if message.author.id == self.bot.user.id:
					await message.edit(view=VoteView(message.embeds[0].title))
			except Exception as excpt:
				print("ERROR")
				print(excpt.__str__())


		while True:
			all_requests_names = [f.split(".")[0] for f in listdir('server_requests')]
			unused_names = all_requests_names
			print(all_requests_names)
			await asyncio.sleep(10)
			council_messages = await council_channel.history(limit=1000).flatten()
			for message in council_messages:
				try:
					if len(message.embeds)>0:
						embed = message.embeds[0]
						if message.author.id==self.bot.user.id and os.path.exists(f'server_requests/{embed.title}.json'):
							if embed.title in unused_names:
								unused_names.remove(embed.title)

							if not message.pinned:
								await message.pin()

							with open(f'server_requests/{embed.title}.json', 'r') as file:
								timestamp: int = json.loads(file.read())['timestamp']
							with open(f'server_requests/{embed.title}.json', 'r') as file:
								voting: Dict[str, int] = json.loads(file.read())['voting']
							with open(f'server_requests/{embed.title}.json', 'r') as file:
								comment: str = json.loads(file.read())['comment']
							if ((datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)).seconds>=60*60*24) or (not (0 in voting.values())) or (list(voting.values()).count(1) > list(voting.values()).count(0)+list(voting.values()).count(2)) or (list(voting.values()).count(2) > list(voting.values()).count(0)+list(voting.values()).count(1)):



								y = 0
								n = 0
								h = 0
								d = 0
								for v in voting.values():
									if v == 1:
										y+=1
									elif v == 2:
										n+=1
									elif v == 3:
										h += 1
									else:
										d += 1



								if y==n:
									await council_channel.send(f"Голосування по запиту {embed.title} завершилось тим, що рада серверу не знайшла однозначного рішення\n\n"
									                           f"❌ Пропозицію не прийнято\n"
									                           f"> - {y} - Підтримали\n"
									                           f"> - {n} - Не підтримали\n"
									                           f"> - {h} - Утримались\n"
									                           f"> - {d} - Не проголосували", embed=discord.Embed(title=embed.title,description=comment, colour=discord.Colour.from_rgb(79,84,92)))
								elif y>n:
									await council_channel.send(f"Голосування по запиту {embed.title} завершилось прийняттям\n\n"
									                           f"✅ Пропозицію прийнято\n"
									                           f"> - {y} - Підтримали\n"
									                           f"> - {n} - Не підтримали\n"
									                           f"> - {h} - Утримались\n"
									                           f"> - {d} - Не проголосували", embed=discord.Embed(title=embed.title,description=comment, colour=discord.Colour.from_rgb(79,84,92)))
								elif n>y:
									await council_channel.send(f"Голосування по запиту {embed.title} завершилось не прийняттям\n\n"
									                           f"❌ Пропозицію не прийнято\n"
									                           f"> - {y} - Підтримали\n"
									                           f"> - {n} - Не підтримали\n"
									                           f"> - {h} - Утримались\n"
									                           f"> - {d} - Не проголосували", embed=discord.Embed(title=embed.title,description=comment, colour=discord.Colour.from_rgb(79,84,92)))

								await message.delete()
								os.replace(f'server_requests/{embed.title}.json',f'ended_requests/{embed.title}.json')
							else:
								with open(f'server_requests/{embed.title}.json', 'r') as file:
									voting: Dict[str,int] = json.loads(file.read())['voting']

								voters = []

								for k, v in voting.items():
									if v!=0:
										voters.append(int(k))

								old_voters_str = embed.fields[1].value
								new_voters_str = '*(ніхто)*'
								if len(voters)>0:
									new_voters_str=''
								for vtr in voters:
									new_voters_str+=f"<@{vtr}> "

								if new_voters_str!=old_voters_str:
									embed.fields[1].value = new_voters_str
									await message.edit(embed = embed)
				except Exception as exception:
					print(exception.__str__())

			print(f'Unused: {unused_names}')
			for request_name in unused_names:
				try:
					embed = discord.Embed(title=request_name)
					with open(f'server_requests/{request_name}.json', 'r') as file:
						request_info: Dict[str, Any] = json.loads(file.read())

					start_timestamp= request_info['timestamp']
					author_id= request_info['author_id']
					if 'voting' in request_info:
						del(request_info['voting'])
						del(request_info['timestamp'])
						del(request_info['author_id'])
					embed.description=''
					nl = '\n'
					for k,v in request_info.items():
						embed.description+=f"\n- {k}\n> {v.replace(nl, nl+'> ')}"
					embed.add_field(name="Кінець голосування: ",
					                value=f'<t:{round((datetime.datetime.fromtimestamp(start_timestamp)+datetime.timedelta(seconds=60*60*24)).timestamp())}:R> (<t:{round((datetime.datetime.fromtimestamp(start_timestamp)+datetime.timedelta(seconds=60*60*24)).timestamp())}:d> <t:{round((datetime.datetime.fromtimestamp(start_timestamp)+datetime.timedelta(seconds=60*60*24)).timestamp())}:t>)')
					embed.add_field(name="Проголосували: ",
					                value=f'*(ніхто)*')
					embed.add_field(name="Створив запит: ",
					                value=f'<@{author_id}>')

					uids_str = ''
					for member in (await council_channel.guild._fetch_role(council_role_id)).members:
						uids_str+=f"><@{member.id}> "
					await council_channel.send(f'Можуть проголосувати: \n{uids_str}',embed=embed,view=VoteView(request_name, timeout=None))
				except Exception as e:
					print(e.__str__())

	@discord.slash_command()  # we can also add application commands
	async def request(self, ctx: discord.ApplicationContext):




		if ctx.guild.id == 1208129686031310848:
	
			server_council_ids = []
	
			for member in (await ctx.guild._fetch_role(council_role_id)).members:
				server_council_ids.append(member.id)


			with open(f'data/last_requests.json' ,'r') as file:
				last_requests = json.loads(file.read())

			if (str(ctx.author.id) in last_requests) and not (ctx.author.id in server_council_ids):
				if (datetime.datetime.now()- datetime.datetime.fromtimestamp(last_requests[str(ctx.author.id)])).seconds<60*60*24:
					await ctx.respond(f"Не радники можуть створювати лише 1 запит на добу. Наступний запит ви зможете створити: <t:{round((datetime.datetime.fromtimestamp(last_requests[str(ctx.author.id)])+datetime.timedelta(seconds=60*60*24)).timestamp())}:R>", ephemeral=True)
					return
			await ctx.respond(view=RequestView(server_council_ids))


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(ServerCouncil(bot))  # add the cog to the bot
