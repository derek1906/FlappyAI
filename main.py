import argparse
import pygame
import os
import sys
import pickle
from flappy import FlappyGame
from qlearning import Trainer, ModelInterface

qtable_filename = "qtable.p"

# interface for Trainer
class FlappyInterface(ModelInterface):
	def __init__(self, game, log_events=False):
		self.game = game
		self.prev_state = None
		self.prev_action = 0
		self.prev_reward = 0
		game.external_draw = self.render

		if log_events:
			for event_name in FlappyGame.get_events():
				game.events.add(event_name, self.event_handler)
		
	def step(self, action):
		if action == FlappyGame.QUIT:
			# request trainer to terminate
			return ModelInterface.REQUEST_TERMINATE

		self.prev_state = self.get_state()

		sum_reward = 0
		for i in xrange(0, 10):
			status = self.game.step(action if i == 0 else FlappyGame.NONE)
			rewards = {
				FlappyGame.NORMAL: 0,
				FlappyGame.PASSED: 300,
				FlappyGame.COLLIDED: -300,
				FlappyGame.QUIT: 0	# should not reach
			}
			reward = rewards[status]
			sum_reward += reward

		self.prev_action = action
		self.prev_reward = sum_reward
		return sum_reward

	def get_actions(self):
		return self.game.get_actions()

	def get_all_states(self):
		states = []
		'''
		States:
		- Horizontal distance between bird and nearest pipe (0 to 300 / 5 or 300+)
		- Vertical distance between bird and nearest pipe (-height / 5 to height / 5)
		- Bird velocity (-10 / 5 to 20 / 5)
		'''
		for horizontal_distance in xrange(0, (300 / 10 + 1) + 1):
			for vertical_distance in xrange(-self.game.height / 10, (self.game.height / 10) + 1):
				for velocity in xrange(-10 / 5, (20 / 5) + 1):
					states.append((horizontal_distance, vertical_distance, velocity))

		return states

	def get_state(self):
		next_pipe = self.game.get_next_pipe()
		distance_to_next_pipe = min(next_pipe.x - self.game.progress, 300 + 10)
		distance_to_pipe_space = 0 if (distance_to_next_pipe > 300) else (self.game.bird.y - next_pipe.space_y)
		return (
			int(distance_to_next_pipe) / 10,
			int(distance_to_pipe_space) / 10,
			int(self.game.bird.velocity) / 5
		)

	def render(self, game):
		state_text = game.game_font.render(str(self.prev_state), False, (255, 255, 255))
		reward_text = game.game_font.render("action: %d reward: %d" % (self.prev_action, self.prev_reward), False, (255, 255, 255))
		game.game_screen.blit(state_text, (0, game.height - 30))
		game.game_screen.blit(reward_text, (0, game.height - 60))

	def event_handler(self, event_name, *values):
		if event_name == FlappyGame.GAME_ENDED:
			print("Score: %d" % values[0]["final_score"])

def interactive(game):
	# interactive mode
	while True:
		status = game.step()
		if status == FlappyGame.QUIT:
			break


def train(game, alpha, gamma, epsilon):
	# training mode
	trainer = Trainer(FlappyInterface(game), alpha, gamma, epsilon)
	trainer.train()


def test(game):
	# testing mode
	trainer = Trainer(FlappyInterface(game, True))
	trainer.evaluate()

def main():
	parser = argparse.ArgumentParser(description="FlappyAI - AI trying to learn how to play a Flappy Bird clone.", formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("mode", choices=["interactive", "train", "test"], nargs="?", default="interactive",
		help="program mode\n\ninteractive: human playing\nlearn: start training\ntest: let computer play")
	parser.add_argument("--show", "-s", dest="display", action="store_true", help="Show window")
	parser.add_argument("--width", dest="width", required=False, default=640, help="interactive window width")
	parser.add_argument("--height", dest="height", required=False, default=480, help="interactive window height")
	parser.add_argument("--alpha", dest="alpha", required=False, default=0.95, help="decay constant")
	parser.add_argument("--gamma", dest="gamma", required=False, default=0.4, help="discount factor")
	parser.add_argument("--epsilon", dest="epsilon", required=False, default=0.5, help="probability of randomness")

	args = parser.parse_args()

	game = FlappyGame(args.width, args.height, args.display or args.mode != "train")

	if args.mode == "interactive":
		interactive(game)
	elif args.mode == "train":
		train(game, float(args.alpha), float(args.gamma), float(args.epsilon))
	elif args.mode == "test":
		test(game)
		
	print("Shutting down...")

if __name__ == "__main__":
	main()