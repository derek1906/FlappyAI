import argparse
import pygame
import os
import sys
import pickle
from flappy import FlappyGame
from trainer import Trainer, ModelInterface

qtable_filename = "qtable.p"

def interactive(game):
	# interactive mode
	while True:
		status = game.step()
		if status == FlappyGame.QUIT:
			break

def train(game, alpha, gamma, epsilon):
	# training mode
	class FlappyInterface(ModelInterface):
		def step(self, action):
			status = game.step(action)
			rewards = {
				FlappyGame.NORMAL: 0,
				FlappyGame.PASSED: 100,
				FlappyGame.COLLIDED: -300,
				FlappyGame.QUIT: 0	# should not reach
			}
			return rewards[status]

		def get_actions(self):
			return game.get_actions()

		def get_all_states(self):
			states = []
			'''
			States:
			- Horizontal distance between bird and nearest pipe (0 to 300 / 5 or 300+)
			- Vertical distance between bird and nearest pipe (-height / 5 to height / 5)
			- Bird velocity (-10 / 5 to 20 / 5)
			'''
			for horizontal_distance in xrange(0, (300 / 5 + 1) + 1):
				for vertical_distance in xrange(-game.height / 5, (game.height / 5) + 1):
					for velocity in xrange(-10 / 5, (20 / 5) + 1):
						states.append((horizontal_distance, vertical_distance, velocity))

			return states

		def get_state(self):
			next_pipe = game.get_next_pipe()
			return (
				int(min(next_pipe.x - game.progress, 300 + 5)) / 5,
				int(game.bird.y - next_pipe.space_y) / 5,
				int(game.bird.velocity) / 5
			)

	trainer = Trainer(FlappyInterface(), alpha, gamma, epsilon)
	trainer.train()



def test(game):
	# testing mode
	if not os.path.isfile(qtable_filename):
		print("Cannot find qtable file.")
		sys.exit(1)

def main():
	parser = argparse.ArgumentParser(description="FlappyAI - AI trying to learn how to play a Flappy Bird clone.", formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("mode", choices=["interactive", "train", "test"], nargs="?", default="interactive",
		help="program mode\n\ninteractive: human playing\nlearn: start training\ntest: let computer play")
	parser.add_argument("--width", dest="width", required=False, default=640, help="interactive window width")
	parser.add_argument("--height", dest="height", required=False, default=480, help="interactive window height")
	parser.add_argument("--alpha", dest="alpha", required=False, default=0.9, help="decay constant")
	parser.add_argument("--gamma", dest="gamma", required=False, default=0.4, help="discount factor")
	parser.add_argument("--epsilon", dest="epsilon", required=False, default=0.2, help="probability of randomness")

	args = parser.parse_args()

	game = FlappyGame(args.width, args.height, args.mode == "interactive")

	if args.mode == "interactive":
		interactive(game)
	elif args.mode == "train":
		train(game, args.alpha, args.gamma, args.epsilon)
	elif args.mode == "test":
		test(game)
		
	print("Shutting down...")

if __name__ == "__main__":
	main()