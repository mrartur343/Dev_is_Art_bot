import json


def vote(vid: int, choice: int):
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
		if not (v in choices):
			choices[v] = 1
		else:
			choices[v] += 1

	return choices
