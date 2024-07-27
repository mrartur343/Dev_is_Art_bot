import json
from typing import Tuple, List


def vote(vid: int, choice: List[int]):
	with open('data/vote.json', 'r') as file:
		votes = json.loads(file.read())

	votes[str(vid)] = choice

	with open('data/vote.json', 'w') as file:
		json.dump(votes, file)


def calculate_voices():
	with open('data/vote.json', 'r') as file:
		votes = json.loads(file.read())

	choices = {}

	for k, v in votes.items():
		for v2 in v:
			if not (v2 in choices):
				choices[v2] = 1
			else:
				choices[v2] += 1

	return choices
