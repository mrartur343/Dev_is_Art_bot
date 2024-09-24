import datetime
import json
import os.path
from typing import List

import discord




class OwnRequest(discord.ui.View):
	def __init__(self,server_council_ids:List[int], *args, **kwargs) -> None:
		self.request_tmp_id = str(round(datetime.datetime.now().timestamp()))
		super().__init__(timeout=None,*args, **kwargs)
		with open(f'tmp_requests/{self.request_tmp_id}.json' ,'w') as file:
			voting = {}
			for uid in server_council_ids:
				voting[str(uid)] = None
			json.dump({"name":"",'comment':'','voting':voting,'timestamp':round(datetime.datetime.now().timestamp())}, file)

	@discord.ui.button(label="Назва", style=discord.ButtonStyle.gray, emoji='✏️')
	async def button_callback(self, button, interaction: discord.Interaction):
		await interaction.response.send_modal(StrInput(self.request_tmp_id, 'name', self.message))
	@discord.ui.button(label="Коментар", style=discord.ButtonStyle.gray,emoji='✏️')
	async def button_callback3(self, button, interaction: discord.Interaction):
		await interaction.response.send_modal(StrInput(self.request_tmp_id,'comment',self.message))
	@discord.ui.button(label="Готово", style=discord.ButtonStyle.green,emoji='✅')
	async def button_callback2(self, button, interaction: discord.Interaction):

		with open(f'tmp_requests/{self.request_tmp_id}.json', 'r') as file:
			request = json.loads(file.read())

		os.remove(f'tmp_requests/{self.request_tmp_id}.json')

		request_name =request['name']

		if request['comment']=='':
			await interaction.respond("Ви не ввели коментар до запиту, введіть туди вашу ідею яку ви хочете донести в раду серверу!", ephemeral=True)
		if request_name!='' and not os.path.exists(f'server_requests/{request_name}.json'):
			del(request['name'])
			self.disable_all_items()
			await self.message.edit(view=self)
			request['timestamp'] = round(datetime.datetime.now().timestamp())
			with open(f'server_requests/{request_name}.json' ,'w') as file:
				json.dump(request, file)

			await interaction.respond("Запит успішно створено! Чекайте на його прийняття радою серверу")
		else:
			await interaction.respond("Помилка! Ви або не ввели назву запиту або запит з такою назвою вже існує!", ephemeral=True)

class StrInput(discord.ui.Modal):
	def __init__(self,request_tmp_id:str,request_option:str,or_message : discord.Message, *args, **kwargs) -> None:
		super().__init__(title=request_option,*args, **kwargs)
		self.or_message = or_message
		self.request_tmp_id = request_tmp_id
		self.request_option = request_option
		self.add_item(discord.ui.InputText(label="Введіть текст:", style=discord.InputTextStyle.long))

	async def callback(self, interaction: discord.Interaction):
		with open(f'tmp_requests/{self.request_tmp_id}.json' ,'r') as file:
			server_request = json.loads(file.read())
		server_request[self.request_option]=self.children[0].value
		or_embed: discord.Embed = self.or_message.embeds[0]
		i=-1
		for f in or_embed.fields:
			i+=1
			if f.name==self.request_option:
				or_embed.set_field_at(i,name=self.request_option,value=self.children[0].value)

		with open(f'tmp_requests/{self.request_tmp_id}.json', 'w') as file:
			json.dump(server_request,file)
		await self.or_message.edit(embeds=[or_embed])
		await interaction.respond(f"Успішно змінено {self.request_option}!", ephemeral=True)