import json
import ast
import sys
import numpy as np
from pettingzoo.classic import tictactoe_v3
from TicTacToeAgent import TicTacToeAgent
# from Minimax import minimax
from Minimax_ import Minimax
import time

# dqn
# cleanrl repo

def load(type):
	data_o = {}
	with open('data/table'+type+'.json', 'r') as fp:
		data = json.load(fp)
		for key, value in data.items():
			key = ast.literal_eval(key)
			value = np.array(value)
			data_o[key] = value
	return data_o

def dump(table, type):
	json_table = {}
	for key, value in table.items():
		json_table[str(key)] = value.tolist()
		
	with open('table'+type+'.json', 'w') as fp:
		json.dump(json_table, fp, indent=4)

def merge_states(obs):
	state_p = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
	for t1 in range(len(obs)):
		for t2 in range(len(obs[0])):
			if obs[t1, t2, 0] == 1:
				state_p[t1][t2] = 1
			elif obs[t1, t2, 1] == 1:
				state_p[t1][t2] = 2

	return tuple(map(tuple, state_p))

def qlearning():
	obs, reward[p_id], done[p_id], _, _ = env.last()
	episode_reward[p_id] += reward[p_id]
	new_state_p[p_id] = merge_states(env.observe('player_1')['observation'])
	p[p_id].update(state_p[p_id], new_state_p[p_id], actions[p_id], reward[p_id], gamma)
	state_p[p_id] = new_state_p[p_id]
	if done[p_id]:
		actions[p_id] = None
	else:
		actions[p_id] = p[p_id].get_epsilon_action(obs, new_state_p[p_id])
	env.step(actions[p_id])

def play():
	obs, reward[p_id], done[p_id], _, _ = env.last()
	episode_reward[p_id] += reward[p_id]
	new_state_p[p_id] = merge_states(env.observe('player_1')['observation'])
	state_p[p_id] = new_state_p[p_id]
	if done[p_id]:
		actions[p_id] = None
	else:
		actions[p_id] = p[p_id].get_best_action(obs, new_state_p[p_id])
	print('final action q', actions[p_id])
	env.step(actions[p_id])

def randomized():
	obs, reward[p_id], done[p_id], _, _ = env.last()
	episode_reward[p_id] += reward[p_id]
	if done[p_id]:
		actions[p_id] = None
	else:
		actions[p_id] = p[p_id].get_random_action(obs)
	env.step(actions[p_id])

def minimaxed():
	obs, _, done[p_id], _, _ = env.last()
	minimax_state_p = merge_states(env.observe('player_1')['observation'])
	# actions[p_id] = minimax(obs, p[p_id].qtable, minimax_state_p, 0, True, -1, 1)[0]
	mm = Minimax()
	if done[p_id]:
		actions[p_id] = None
	else:
		actions[p_id] = mm.search(obs, p[p_id].qtable, minimax_state_p, 0, True, -1, 1)[0]
	print('final action minimax', actions[p_id])
	# print(minimax_state_p)
	env.step(actions[p_id])

def interactive():
	env.render()
	print('Make an action: Top left is 0, bottom left is 2, top right is 6, bottom right is 8. PASS if it is a draw')
	actions[p_id] = input().lower()
	if actions[p_id] == 'pass':
		env.step(None)
	else:
		env.step(int(actions[p_id]))

max_episodes = 10000
max_steps = 100
learning_rate = 0.1
gamma = 0.99 #discount rate
epsilon = 0.99
max_epsilon = 1
min_epsilon = 0.01
epsilon_decay_rate = 0.0001
rewards_global_0 = []
rewards_global_1 = []
env = tictactoe_v3.env('human')
env.reset()
np.random.seed(57)
# static_qtable1 = load('1') #pid '1', '2', or 'merged'
# static_qtable2 = load('2')
static_qtablemerged = load('merged')

p = [TicTacToeAgent(learning_rate, epsilon, epsilon_decay_rate, qtable=static_qtablemerged), TicTacToeAgent(learning_rate, epsilon, epsilon_decay_rate, qtable=static_qtablemerged)]
p_id = 0

# convolusion on dqn with the multidimensional boards

for episode in range(max_episodes):
	print('episode', episode)
	env.reset()
	state_p = [None, None]
	new_state_p = [None, None]
	actions = [None, None]
	reward = [0, 0]
	done = [False, False]
	episode_reward = [0, 0]
	round = 0

	for agent in env.agent_iter(max_steps):
		time.sleep(1)
		# print(reward[1])
		if agent == 'player_1':
			p_id = 0
			play()
			if done[1]:
				time.sleep(2)
				break
		if agent == 'player_2':
			p_id = 1
			minimaxed()
			if done[0]:
				time.sleep(2)
				break

	p[0].decay_epsilon(min_epsilon)
	p[1].decay_epsilon(min_epsilon)

	rewards_global_0.append(episode_reward[0])
	rewards_global_1.append(episode_reward[1])

n = 1000
rewards_per_n_episodes_0 = np.split(np.array(rewards_global_0), max_episodes/n)
rewards_per_n_episodes_1 = np.split(np.array(rewards_global_1), max_episodes/n)
print('Player1:')
for rewards in rewards_per_n_episodes_0:
	print(n, "-> ", str(sum(rewards/1000)), sep='')
	n += 1000
n = 1000
print('Player2:')
for rewards in rewards_per_n_episodes_1:
	print(n, "-> ", str(sum(rewards/1000)), sep='')
	n += 1000

# dump(p[0].qtable, '1') #pid '1', '2', or 'merged'
# dump(p[1].qtable, '2') #pid '1', '2', or 'merged'