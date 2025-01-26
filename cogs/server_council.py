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
	(discord.Embed(title="Ролі й посади",
	               fields=[discord.EmbedField(name='add_roles', value=''), discord.EmbedField(name='remove_roles', value='')])
	 , server_request_inputs.RolesChange)
]

request_cooldown = 60*30
accept_cooldown = 60*60*12

council_role_id = 1321571484401012797

not_asignable_roles = [1321571484401012797, 1321575209785888875]

council_channel_id = 1327376964163604490

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
	def __init__(self,server_council_ids, queue_mode: bool = False, *args, **kwargs):
		self.server_council_ids=server_council_ids
		self.queue_mode = queue_mode
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
				label="Ролі й посади",
				description="Додати або забрати ролі у людини",
				value='1',
				emoji='🚩'
			),
			discord.SelectOption(
				label="Демократія (скоро)",
				description="Дострокові вибори, переобрання міністрів, тощо",
				value='2',
				emoji='🪧'
			)
		]
	)
	async def select_callback(self, select: discord.ui.Select,
	                          interaction: discord.Interaction):  # the function called when the user is done selecting options

		if select.values[0] in ["2"]:
			await interaction.respond("Ці види пропозицій будуть додані вже скоро!",ephemeral=True)


		action = actions[int(select.values[0])]
		roles_str =''
		if int(select.values[0])==0:
			await interaction.respond(embed=discord.Embed(title="Власна пропозиція",
	               fields=[discord.EmbedField(name='name', value=''), discord.EmbedField(name='public', value='True')])
	 , view=server_request_inputs.OwnRequest(self.server_council_ids, interaction.user.id, self.queue_mode))


		elif int(select.values[0])==1:
			embed = discord.Embed(title="Ролі й посади",
	               fields=[discord.EmbedField(name='add_roles', value=''), discord.EmbedField(name='remove_roles', value=''), discord.EmbedField(name='target', value=''), discord.EmbedField(name='public', value='True')])

			role_i = 0
			roles_nums = {}
			for role in await interaction.guild.fetch_roles():
				if role.id in not_asignable_roles or not (role.is_assignable()):
					continue
				roles_str+=f'\n{role_i} - <@&{role.id}>'
				roles_nums[role_i]=role.id
				role_i+=1
			embed.description=f'Щоб задати які ролі додати чи видалити напишіть всі номера ролей (знизу всі номера) через пробіл\n{roles_str}'



			await interaction.respond(embed =embed, view=server_request_inputs.RolesChange(self.server_council_ids, interaction.user.id,roles_nums, self.queue_mode))


class ServerCouncil(commands.Cog):

	def __init__(self, bot):  # this is a special method that is called when the cog is loaded
		self.bot: discord.Bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		council_channel = self.bot.get_channel(council_channel_id)


		council_messages = await council_channel.history(limit=1000).flatten()

		while True:
			try:
				all_requests_names_queue = [f.split(".")[0] for f in listdir('requests_queue')]
				for r_name in all_requests_names_queue:
					with open(f'requests_queue/{r_name}.json', 'r') as file:
						queue_request_info = json.loads(file.read())

					server_council_ids = []

					for member in (await council_channel.guild._fetch_role(council_role_id)).members:
							server_council_ids.append(member.id)

					with open(f'data/last_requests.json', 'r') as file:
							last_requests = json.loads(file.read())

					r_author_id  = queue_request_info['author_id']

					ended_queue = True

					if (str(r_author_id) in last_requests) and not (r_author_id in server_council_ids):
						if (datetime.datetime.now().timestamp() - last_requests[str(r_author_id)]) > request_cooldown:
							ended_queue=False
					if True:
						if ended_queue:
							os.remove(f'requests_queue/{r_name}.json')


							queue_request_info['timestamp'] = round(datetime.datetime.now().timestamp())
							with open(f'server_requests/{r_name}.json', 'w') as file:
								json.dump(queue_request_info, file)

							with open(f'data/last_requests.json', 'r') as file:
								last_requests = json.loads(file.read())

							last_requests[str(r_author_id)] = round(datetime.datetime.now().timestamp())

							with open(f'data/last_requests.json', 'w') as file:
								json.dump(last_requests, file)


			except:
				pass

			try:
				all_requests_names = [f.split(".")[0] for f in listdir('server_requests')]
				unused_names = all_requests_names
				print(all_requests_names)
				council_messages = await council_channel.history(limit=1000).flatten()
				for message in council_messages:
					try:
						if len(message.embeds)>0:
							embed = message.embeds[0]
							if message.author.id==self.bot.user.id and os.path.exists(f'server_requests/{embed.title}.json'):
								await message.edit(view=VoteView(message.embeds[0].title))
								if embed.title in unused_names:
									unused_names.remove(embed.title)

								if not message.pinned:
									await message.pin()
								with open(f'server_requests/{embed.title}.json', 'r') as file:
									server_request_dict = json.loads(file.read())

								timestamp: int = server_request_dict['timestamp']
								voting: Dict[str, int] = server_request_dict['voting']
								if 'comment' in server_request_dict:
									comment: str = server_request_dict['comment']
								elif 'add_roles' in server_request_dict:
									add_roles_str = server_request_dict['add_roles']
									if len(add_roles_str)>0:
										if add_roles_str[-1]==' ':
											add_roles_str = add_roles_str[:-1]
									add_roles_id: List[int] = add_roles_str.split(" ")
									if len(add_roles_id)==1:
										if add_roles_id[0]=='':
											add_roles_id.pop(0)
									print(add_roles_id)
									remove_roles_str = server_request_dict['remove_roles']
									if len(remove_roles_str)>0:
										if remove_roles_str[-1]==' ':
											remove_roles_str = remove_roles_str[:-1]
									remove_roles_id: List[int] = remove_roles_str.split(" ")
									if len(remove_roles_id)==1:
										if remove_roles_id[0]=='':
											remove_roles_id.pop(0)
									print(remove_roles_id)
									comment = ''

									for role_id in add_roles_id:
										comment+=f'\n Додати <@&{role_id}>'

									comment+='\n'

									for role_id in remove_roles_id:
										comment+=f'\n Забрати <@&{role_id}>'

								print(f"Time check for {embed.title} - {(datetime.datetime.now().timestamp() - timestamp)-accept_cooldown} seconds")
								if ((datetime.datetime.now().timestamp() - timestamp)>=accept_cooldown) or (not (0 in voting.values())) or (list(voting.values()).count(1) > list(voting.values()).count(0)+list(voting.values()).count(2)) or (list(voting.values()).count(2) > list(voting.values()).count(0)+list(voting.values()).count(1)):
									print(f"END {embed.title}")


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
										if 'add_roles' in server_request_dict:
											target_member = await council_channel.guild.fetch_member(server_request_dict['target'])

											add_roles: List[discord.Role] = []
											for role_id in add_roles_id:
												await target_member.add_roles(await council_channel.guild._fetch_role(int(role_id)))

											remove_roles: List[discord.Role] = []
											for role_id in remove_roles_id:
												await target_member.remove_roles(await council_channel.guild._fetch_role(int(role_id)))



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
						public= request_info['public']
						if 'voting' in request_info:
							del(request_info['voting'])
							del(request_info['timestamp'])
							del(request_info['author_id'])
							del(request_info['public'])
						embed.description=''
						nl = '\n'
						if 'comment' in request_info:
							for k,v in request_info.items():
								v = str(v)
								embed.description+=f"\n- {k}\n> {v.replace(nl, nl+'> ')}"
						else:
							add_roles_id: List[int] = request_info['add_roles'].split(" ")
							remove_roles_id: List[int] = request_info['remove_roles'].split(" ")
							target: int = request_info['target']
							comment = f'Змінити ролі для <@{target}>'

							comment += '\n'

							for role_id in add_roles_id:
								if role_id!='':
									comment += f'\n Додати <@&{role_id}>'

							comment += '\n'

							for role_id in remove_roles_id:
								if role_id!='':
									comment += f'\n Забрати <@&{role_id}>'

							embed.description=comment

						embed.add_field(name="Кінець голосування: ",
						                value=f'<t:{round((datetime.datetime.fromtimestamp(start_timestamp)+datetime.timedelta(seconds=accept_cooldown)).timestamp())}:R> (<t:{round((datetime.datetime.fromtimestamp(start_timestamp)+datetime.timedelta(seconds=accept_cooldown)).timestamp())}:d> <t:{round((datetime.datetime.fromtimestamp(start_timestamp)+datetime.timedelta(seconds=accept_cooldown)).timestamp())}:t>)')
						embed.add_field(name="Проголосували: ",
						                value=f'*(ніхто)*')
						embed.add_field(name="Створив запит: ",
						                value=f'<@{author_id}>' if public else 'Анонімний користувач')

						uids_str = ''
						for member in (await council_channel.guild._fetch_role(council_role_id)).members:
							uids_str+=f"<@{member.id}> "
						await council_channel.send(f'Можуть проголосувати: \n{uids_str}',embed=embed,view=VoteView(request_name, timeout=None))
					except Exception as e:
						print("ERROR")
						print(e.__str__())
				await asyncio.sleep(60)
			except Exception as e:
				with open(f'ERROR_LOG_{round(datetime.datetime.now().timestamp())}.json', 'w') as file:
					json.dump(['Error in cycle start', e.__str__(), datetime.datetime.now().strftime("%c")],file)

	@discord.slash_command()  # we can also add application commands
	async def request(self, ctx: discord.ApplicationContext):




		server_council_ids = []

		for member in (await ctx.guild._fetch_role(council_role_id)).members:
			server_council_ids.append(member.id)


		with open(f'data/last_requests.json' ,'r') as file:
			last_requests = json.loads(file.read())
		queue_mode = False

		if (str(ctx.author.id) in last_requests) and not (ctx.author.id in server_council_ids):
			if (datetime.datetime.now().timestamp() - last_requests[str(ctx.author.id)])<request_cooldown:
				await ctx.respond(f"Не радники можуть створювати лише 1 запит на півгодини. Запит буде додано до черги. Тоді ваш запит з черги буде відправлено: <t:{round((datetime.datetime.fromtimestamp(last_requests[str(ctx.author.id)])+datetime.timedelta(seconds=request_cooldown)).timestamp())}:R>", ephemeral=True)
				queue_mode=True
		await ctx.respond(view=RequestView(server_council_ids, queue_mode))


def setup(bot):  # this is called by Pycord to setup the cog
	bot.add_cog(ServerCouncil(bot))  # add the cog to the bot
