#!/usr/bin/python
# -*- coding: utf8 -*-

import signal
import cPickle as pickle
import os
import random
from datetime import datetime

qtable_filename = "qtable.p"


def better_max(lst, func):
	if len(lst) == 0:
		return None

	max_items = [lst[0]]
	max_val = func(lst[0])
	for item in lst:
		val = func(item)
		if val > max_val:
			max_val = val
			max_items = [item]
		elif val == max_val:
			max_items.append(item)

	return {
		"item": random.choice(max_items),
		"value": max_val
	}


class Trainer:
	def sigint_handler(self, signal, frame):
		self.sigint = True

	def __init__(self, model, alpha=0, gamma=0, epsilon=0):
		# Initialize signal handler
		signal.signal(signal.SIGINT, self.sigint_handler)
		self.sigint = False

		self.qtable = {}
		self.train_count = 0
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon

		self.model = model

		if os.path.isfile(qtable_filename):
			# load from save file
			print("Loading from pickle file...")
			with open(qtable_filename, "rb") as f:
				save_file = pickle.load(f)
				self.qtable = save_file["qtable"]
				self.train_count = save_file["train_count"]
				#self.alpha = save_file["alpha"]
				#self.gamma = save_file["gamma"]
				#self.epsilon = save_file["epsilon"]
		else:
			# init Q table
			print("Initializing states...")
			for state in model.get_all_states():
				for action in model.get_actions():
					self.qtable[(action, state)] = 0.0

	def train(self):
		print(u"Training started, using α=%.1f γ=%.1f ε=%.1f." % (self.alpha, self.gamma, self.epsilon))
		while True:
			if self.sigint:
				break

			self.train_count += 1

			if self.train_count % 1000000 == 0:
				print("[{}] Step #{}".format(str(datetime.now()), self.train_count))

			state = self.model.get_state()
			action = self.f_function(state)
			reward = self.model.step(action)
			new_state = self.model.get_state()

			q = self.qtable[(action, state)]
			max_q_prime = better_max(self.model.get_actions(), lambda action: self.qtable[(action, new_state)])["value"]

			self.qtable[(action, state)] = q + self.alpha * (reward + self.gamma * max_q_prime - q)

		# store trained Q table
		print("Storing pickle file...")
		with open(qtable_filename, "wb") as f: 
			save_obj = {
				"qtable": self.qtable,
				"train_count": self.train_count,
				"alpha": self.alpha,
				"gamma": self.gamma,
				"epsilon": self.epsilon
			}
			pickle.dump(save_obj, f)

	def evaluate(self):
		print("Evaluation started.")

		# disable exploration
		self.epsilon = 0

		while True:
			if self.sigint:
				break

			state = self.model.get_state()
			action = self.f_function(state)
			self.model.step(action)

	def f_function(self, state):
		'''
		Choose action based on an epsilon greedy approach
		return action selected
		'''
		action_selected = None

		# Your Code Goes Here!
		
		if random.random() < self.epsilon:
			# Pick a random action
			action_selected = random.choice(self.model.get_actions())
		else:
			action_selected = better_max(self.model.get_actions(), lambda action: self.qtable[(action, state)])["item"]
		
		return action_selected
			

class ModelInterface:
	'''
	Step function. Returns reward value.
	'''
	def step(self, action):
		return 0

	'''
	Get available actions.
	'''
	def get_actions(self):
		return [0]

	'''
	Initialize states
	'''
	def get_all_states(self):
		return {}

	'''
	Get current state
	'''
	def get_state(self):
		return ()
