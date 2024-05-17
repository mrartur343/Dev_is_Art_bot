import datetime
import random
import jmespath
import typing
from modules import radio_timetable

import discord

radio_vote_msg: None | discord.Message = None
vote_emojies = ['🇦', '🇧', '🇬']

async def create_radio_vote(radio_info: discord.VoiceChannel):
	global radio_vote_msg
	radio_vote_msg= await radio_info.send(embed=discord.Embed(title='load...'))


async def update_radio_vote(albums_names: typing.List[str], singles_names: typing.List[str],
							durations: typing.Dict[str, int], albums_full_names: typing.Dict[str,str],next_cycle_time: datetime.datetime):
	global radio_vote_msg

	albums_names_variations = []
	singles_names_variations = []

	timetables_variations = []
	radio_channels = []

	for i in range(3):
		random.shuffle(albums_names)
		random.shuffle(singles_names)
		albums_names_variations.append(albums_names[:2])
		singles_names_variations.append(singles_names[:2])

	i = 0


	for albums_names, singles_names in zip(albums_names_variations, singles_names_variations):
		album_list = []
		st = datetime.datetime.now()
		for short_name in albums_names:

			st += datetime.timedelta(seconds=durations[short_name])
			album_list.append(short_name)
			for _ in range(2):
				if i >= len(singles_names):
					i = 0
				st += datetime.timedelta(seconds=durations[singles_names[i]])
				album_list.append(singles_names[i])
				i += 1
		radio_channels.append(album_list)
		timetable = radio_timetable.get_album_times(album_list, durations, -1, next_cycle_time)
		timetables_variations.append(timetable)

	if not (radio_vote_msg is None):
		radio_channel_vote_names = ['Alpha', 'Beta', "Gamma"]

		vote_embed = discord.Embed(title='Вибрати радіо')
		vote_embed.description = "Часто на радіо зустрічалась проблема того, що на радіо грають альбоми які мало подобаються людям в день та які подобаються - вночі.\nЩоб це вирішити ми даємо вам можливість вибрати 1 з 3 варіантів того, які альбоми й у який час будуть грати. Вибране радіо заграє по завершенню попереднього\n"
		l = 0
		for votetimetable in timetables_variations:
			timetable_str = ''
			old_emoji = ''
			single_check = True
			i = 0
			for k, v in votetimetable:

				if i < 6:
					v: datetime.datetime

					kyiv_h = v.hour
					print(kyiv_h)

					time_emoji = "🏙️ " if 12 <= kyiv_h < 18 else (
						"🌇" if 18 <= kyiv_h < 24 else ('🌇' if 6 <= kyiv_h < 12 else "🌃"))
					if time_emoji != old_emoji:
						timetable_str += f"\n- {time_emoji}\n"
					print(f'k: {k}, v: {v} s: {k in singles_names}')
					if i == 0 and (k in singles_names) and single_check:
						single_check = False
						timetable_str += f"⚡ <t:{round(v.timestamp())}:t> Випадковий сингл (<t:{round(v.timestamp())}:R>)\n"
						timetable_str += "-----\n"
					elif (not k in singles_names):
						timetable_str += (
							f"<t:{round(v.timestamp())}:t> {albums_full_names[k]} {f' (<t:{round(v.timestamp())}:R>)' if (i == 0) and single_check else ''}\n")
						i += 1

				old_emoji = time_emoji
			vote_embed.add_field(name=f'Radio {radio_channel_vote_names[l]}', value=timetable_str)
			l += 1

		await radio_vote_msg.edit(embed=vote_embed)

		for vote_e in vote_emojies:
			await radio_vote_msg.add_reaction(vote_e)

		return radio_channels


async def get_vote_results(channel_info: discord.VoiceChannel):
	def sort_r(reaction: discord.Reaction):
		return reaction.count

	if radio_vote_msg is not None:
		react_msg = await channel_info.fetch_message(radio_vote_msg.id)
		reactions = react_msg.reactions
		if len(reactions)==0:
			return None
		print('Reactions not sorted')
		print(reactions)
		reactions.sort(key = sort_r,reverse=True)
		print('Reactions sorted')
		print(reactions)

		print(reactions[0].emoji.__str__())
		radio_channel_index = vote_emojies.index(reactions[0].emoji.__str__())

		return radio_channel_index
	else:
		return None

