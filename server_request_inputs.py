import datetime
import json
import os.path
import typing
from typing import List

import discord




class OwnRequest(discord.ui.View):
	def __init__(self,server_council_ids:List[int],author_id:int, queue_mode:bool=False, *args, **kwargs) -> None:
		self.queue_mode = queue_mode
		self.request_tmp_id = str(round(datetime.datetime.now().timestamp()))
		self.author_id = author_id
		super().__init__(timeout=None,*args, **kwargs)
		with open(f'tmp_requests/{self.request_tmp_id}.json' ,'w') as file:
			voting = {}
			for uid in server_council_ids:
				voting[str(uid)] = 0
			json.dump({"name":"",'comment':'','voting':voting,'public':True,'timestamp':round(datetime.datetime.now().timestamp())}, file)

	@discord.ui.button(label="Назва", style=discord.ButtonStyle.gray, emoji='✏️')
	async def button_callback(self, button, interaction: discord.Interaction):
		if interaction.user.id == self.author_id:
			await interaction.response.send_modal(StrInput(self.request_tmp_id, 'name', self.message,200))
		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
			                          ephemeral=True)
	@discord.ui.button(label="Коментар", style=discord.ButtonStyle.gray,emoji='✏️')
	async def button_callback3(self, button, interaction: discord.Interaction):
		if interaction.user.id == self.author_id:
			await interaction.response.send_modal(StrInput(self.request_tmp_id,'comment',self.message,1950))

		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
	                          ephemeral=True)
	@discord.ui.button(label="Анонімний/відомий автор", style=discord.ButtonStyle.gray,emoji='👁️', custom_id='public_button')
	async def button_callback4(self, button, interaction: discord.Interaction):
		if interaction.user.id == self.author_id:

			with open(f'tmp_requests/{self.request_tmp_id}.json', 'r') as file:
				request = json.loads(file.read())

			if request['public']:
				request['public']=False
			else:
				request['public']=True

			with open(f'tmp_requests/{self.request_tmp_id}.json', 'w') as file:
				json.dump(request, file)

			or_embed: discord.Embed = self.message.embeds[0]
			i = -1
			for f in or_embed.fields:
				i += 1
				if f.name == 'public':
					or_embed.set_field_at(i, name='public', value="🙋 Показати автора запиту"if request['public'] else "🥷 Не показувати автора запиту")

			await self.message.edit(embeds=[or_embed])
			await interaction.respond(f"Успішно змінено анонімність!", ephemeral=True)

		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
	                          ephemeral=True)
	@discord.ui.button(label="Готово", style=discord.ButtonStyle.green,emoji='✅')
	async def button_callback2(self, button, interaction: discord.Interaction):
		if interaction.user.id==self.author_id:

			with open(f'tmp_requests/{self.request_tmp_id}.json', 'r') as file:
				request = json.loads(file.read())

			os.remove(f'tmp_requests/{self.request_tmp_id}.json')

			request_name =request['name']

			if request['comment']=='':
				await interaction.respond("Ви не ввели коментар до запиту, введіть туди вашу ідею яку ви хочете донести в раду серверу!", ephemeral=True)
			elif request_name!='' and not os.path.exists(f'server_requests/{request_name}.json') and not os.path.exists(f'requests_queue/{request_name}.json'):
				del(request['name'])
				self.disable_all_items()
				await self.message.edit(view=self)
				request['author_id'] = interaction.user.id
				request['timestamp'] = round(datetime.datetime.now().timestamp())
				if not self.queue_mode:
					with open(f'server_requests/{request_name}.json' ,'w') as file:
						json.dump(request, file)


					with open(f'data/last_requests.json' ,'r') as file:
						last_requests = json.loads(file.read())

					last_requests[str(interaction.user.id)]= round(datetime.datetime.now().timestamp())


					with open(f'data/last_requests.json' ,'w') as file:
						json.dump(last_requests, file)
					await interaction.respond("Запит успішно створено! Чекайте на його прийняття радою серверу")
				else:
					with open(f'requests_queue/{request_name}.json' ,'w') as file:
						json.dump(request, file)
					await interaction.respond("Запит успішно створено! Його додано у вашу чергу на відправлення запитів у раду. Можна відправляти по 1 запиту на день")




			else:
				await interaction.respond("Помилка! Ви або не ввели назву запиту або запит з такою назвою вже існує!", ephemeral=True)
		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
			                          ephemeral=True)

class RolesChange(discord.ui.View):
	def __init__(self,server_council_ids:List[int],author_id:int,roles_nums, queue_mode:bool=False, *args, **kwargs) -> None:
		self.queue_mode = queue_mode
		self.roles_nums: typing.Dict[int,int] = roles_nums
		self.request_tmp_id = str(round(datetime.datetime.now().timestamp()))
		self.author_id = author_id
		super().__init__(timeout=None,*args, **kwargs)
		with open(f'tmp_requests/{self.request_tmp_id}.json' ,'w') as file:
			voting = {}
			for uid in server_council_ids:
				voting[str(uid)] = 0
			json.dump({"add_roles":"",'remove_roles':'','target':'','public':True,'voting':voting,'timestamp':round(datetime.datetime.now().timestamp())}, file)

	@discord.ui.button(label="Додати ролі", style=discord.ButtonStyle.gray, emoji='✏️')
	async def button_callback(self, button, interaction: discord.Interaction):
		if interaction.user.id == self.author_id:
			await interaction.response.send_modal(StrInput(self.request_tmp_id, 'add_roles', self.message,4000,self.roles_nums))
		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
			                          ephemeral=True)
	@discord.ui.button(label="Забрати ролі", style=discord.ButtonStyle.gray,emoji='✏️')
	async def button_callback3(self, button, interaction: discord.Interaction):
		if interaction.user.id == self.author_id:
			await interaction.response.send_modal(StrInput(self.request_tmp_id,'remove_roles',self.message,4000,self.roles_nums))

		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
	                          ephemeral=True)
	@discord.ui.button(label="У кого", style=discord.ButtonStyle.gray,emoji='✏️')
	async def button_callback4(self, button, interaction: discord.Interaction):
		if interaction.user.id == self.author_id:
			await interaction.response.send_modal(StrInput(self.request_tmp_id,'target',self.message,100))

		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
	                          ephemeral=True)
	@discord.ui.button(label="Анонімний/відомий автор", style=discord.ButtonStyle.gray,emoji='👁️')
	async def button_callback5(self, button, interaction: discord.Interaction):
		if interaction.user.id == self.author_id:

			with open(f'tmp_requests/{self.request_tmp_id}.json', 'r') as file:
				request = json.loads(file.read())

			if request['public']:
				request['public']=False
			else:
				request['public']=True

			with open(f'tmp_requests/{self.request_tmp_id}.json', 'w') as file:
				json.dump(request, file)
		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
	                          ephemeral=True)
	@discord.ui.button(label="Готово", style=discord.ButtonStyle.green,emoji='✅')
	async def button_callback2(self, button, interaction: discord.Interaction):
		if interaction.user.id==self.author_id:

			with open(f'tmp_requests/{self.request_tmp_id}.json', 'r') as file:
				request = json.loads(file.read())

			os.remove(f'tmp_requests/{self.request_tmp_id}.json')


			if request['add_roles']=='' and request['remove_roles']=='':
				await interaction.respond("Ви не написали які ролі необхідно змінити!", ephemeral=True)
			else:
				self.disable_all_items()
				await self.message.edit(view=self)
				request['author_id'] = interaction.user.id
				request['timestamp'] = round(datetime.datetime.now().timestamp())
				with open(f'server_requests/Запит {self.request_tmp_id}.json' ,'w') as file:
					json.dump(request, file)


				with open(f'data/last_requests.json' ,'r') as file:
					last_requests = json.loads(file.read())

				last_requests[str(interaction.user.id)]= round(datetime.datetime.now().timestamp())


				with open(f'data/last_requests.json' ,'w') as file:
					json.dump(last_requests, file)


				await interaction.respond("Запит успішно створено! Чекайте на його прийняття радою серверу")
		else:
			await interaction.respond("Помилка! Це запит іншої людини!",
			                          ephemeral=True)


class StrInput(discord.ui.Modal):
	def __init__(self,request_tmp_id:str,request_option:str,or_message : discord.Message,text_limit:int,roles_nums:typing.Dict[int,int] | None = None, *args, **kwargs) -> None:
		super().__init__(title=request_option,*args, **kwargs)
		self.roles_nums = roles_nums
		self.or_message = or_message
		self.request_tmp_id = request_tmp_id
		self.request_option = request_option

		self.add_item(discord.ui.InputText(label="Введіть текст:", style=discord.InputTextStyle.long,max_length=text_limit))

	async def callback(self, interaction: discord.Interaction):
		with open(f'tmp_requests/{self.request_tmp_id}.json' ,'r') as file:
			server_request = json.loads(file.read())

		or_embed: discord.Embed = self.or_message.embeds[0]
		i=-1
		if self.request_option != 'comment':
			for f in or_embed.fields:
				i+=1
				if f.name==self.request_option:
					if f.name in ['add_roles','remove_roles']:
						all_nums = self.children[0].value.split(' ')
						roles_id = []
						for num in all_nums:
							roles_id.append(self.roles_nums[int(num)])

						server_request[self.request_option] = ""

						for role_id in roles_id:
							server_request[self.request_option] += str(role_id) + " "

						roles_str = ''
						for role_id in roles_id:
							roles_str+=f"\n{'+' if f.name=='add_roles' else '-'} <@&{role_id}>"
						or_embed.set_field_at(i, name=self.request_option, value=roles_str)
					elif f.name == 'target':
						try:
							member_id = interaction.guild.get_member_named(self.children[0].value.replace("@","")).id
							server_request[self.request_option] = member_id
							or_embed.set_field_at(i, name=self.request_option, value=f"<@{member_id}>")
						except:
							await interaction.respond(f"Помилка, оскільки не знайдено такого користувача, спробуйте перевірити нікнейм", ephemeral=True)
							return
					else:
						server_request[self.request_option] = self.children[0].value
						or_embed.set_field_at(i,name=self.request_option,value=self.children[0].value)
		else:
			server_request[self.request_option] = self.children[0].value
			or_embed.description=self.children[0].value
		with open(f'tmp_requests/{self.request_tmp_id}.json', 'w') as file:
			json.dump(server_request,file)
		await self.or_message.edit(embeds=[or_embed])
		await interaction.respond(f"Успішно змінено {self.request_option}!", ephemeral=True)
