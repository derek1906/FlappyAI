import pygame
from collections import deque
import random
from events import EventManager

camera_offset = 100

class FlappyGame:
	'''
	Flappy Bird emulator
	'''
	def __init__(self, width, height, interactive_mode=False):
		self.width = width
		self.height = height
		self.start_height = height / 2
		self.pipe_start_offset = 1000
		self.pipe_distance = 300
		self.pipe_space = 100
		self.pipe_count = 5
		self.horizontal_speed = 5
		self.gravity = 0.5
		self.interactive_mode = interactive_mode
		self.external_draw = None

		self.events = EventManager()

		if interactive_mode:
			# init pygame font
			print("Initializing font... This might take a while.")
			pygame.font.init()
			self.game_font = pygame.font.SysFont("Arial", 30)
			# init pygame clock
			self.game_clock = pygame.time.Clock()
			# init pygame display
			pygame.display.init()
			# set window dimensions
			self.game_screen = pygame.display.set_mode((width, height))
			# set window title
			pygame.display.set_caption("FlappyAI")


		self.reset()

	def reset(self):
		self.progress = 0
		self.score = 0
		self.next_pipe_x_location = self.pipe_start_offset + self.pipe_count * self.pipe_distance
		self.bird = Bird(self.height / 2, self.gravity)
		self.pipes = deque()

		# generate pipes
		for i in xrange(0, self.pipe_count):
			self.pipes.append(Pipe.generate_pipe(self.pipe_start_offset + i * self.pipe_distance, self.height))

	def restart(self):
		self.events.trigger(FlappyGame.GAME_ENDED, {
			"final_score": self.score,
			"final_progress": self.progress
		})
		self.reset()

	def add_new_pipe(self):
		self.pipes.append(Pipe.generate_pipe(self.next_pipe_x_location, self.height))
		self.next_pipe_x_location += self.pipe_distance

	def step(self, action=0):
		if self.interactive_mode:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return FlappyGame.QUIT
				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
					action = FlappyGame.JUMP

		# step forward
		self.bird.step(action)
		self.progress += self.horizontal_speed
		if self.bird.y < 0:
			self.bird.y = 0
		if self.bird.y > self.height:
			self.bird.y = self.height

		# regenerate pipe
		if self.pipes[0].get_screen_x_location(self.progress) < 0:
			self.pipes.popleft()
			self.add_new_pipe()

		# render graphics
		if self.interactive_mode:
			self.render()
			self.game_clock.tick(60)

		# check collision
		if self.bird.y >= self.height or self.bird.y <= 0:
			# hit the ground
			self.restart()
			return FlappyGame.COLLIDED

		upcoming_pipe = self.get_next_pipe()
		if self.progress == upcoming_pipe.x:
			if abs(self.bird.y - upcoming_pipe.space_y) > self.pipe_space / 2:
				# collided
				self.restart()
				return FlappyGame.COLLIDED
			else:
				self.score += 1
				# passed
				return FlappyGame.PASSED

		return FlappyGame.NORMAL

	def render(self):
		self.game_screen.fill((0, 0, 0))

		# draw bird
		pygame.draw.circle(self.game_screen, (255, 255, 255), self.bird.get_screen_location(), 3, 1)

		# draw pipes
		for pipe in self.pipes:
			screen_x_location = pipe.get_screen_x_location(self.progress)
			pygame.draw.line(
				self.game_screen,
				(255, 255, 255),
				(screen_x_location, 0),
				(screen_x_location, pipe.space_y - self.pipe_space / 2)
			)
			pygame.draw.line(
				self.game_screen,
				(255, 255, 255),
				(screen_x_location, pipe.space_y + self.pipe_space / 2),
				(screen_x_location, self.height)
			)

		# draw score
		score_text = self.game_font.render(str(self.score), False, (255, 255, 255))
		score_text_width, score_text_height = self.game_font.size(str(self.score))
		self.game_screen.blit(score_text, (self.width / 2 - score_text_width / 2, 5))
		
		if self.external_draw != None:
			self.external_draw(self)

		pygame.display.flip()

	def get_next_pipe(self):
		for pipe in self.pipes:
			if pipe.x < self.progress:
				continue
			else:
				return pipe

	@staticmethod
	def get_actions():
		return [FlappyGame.JUMP, FlappyGame.NONE]

	@staticmethod
	def get_events():
		return [FlappyGame.GAME_ENDED]

	# step return status
	NORMAL, PASSED, COLLIDED, QUIT = range(4)
	# actions
	NONE, JUMP = range(2)
	# events
	GAME_ENDED = 0


class Bird:
	def __init__(self, y, gravity):
		self.y = y
		self.velocity = 0
		self.jump_velocity = -7
		self.gravity = gravity

	def step(self, action=FlappyGame.NONE):
		if action == FlappyGame.JUMP:
			self.velocity = self.jump_velocity

		self.y += self.velocity
		self.velocity += self.gravity

	def get_screen_location(self):
		return (camera_offset, int(self.y))

class Pipe:
	def __init__(self, x, space_y):
		self.x = x
		self.space_y = space_y

	def get_screen_x_location(self, game_x_location):
		return camera_offset + self.x - game_x_location

	@staticmethod
	def generate_pipe(x, screen_height):
		half_screen_height = screen_height / 2
		pipe = Pipe(x, half_screen_height + random.randint(-half_screen_height, half_screen_height) / 2)
		return pipe