import pygame
from pygame.locals import*
pygame.init()

from libs.World import World

import time


# ====== CLASSES ======
class Main(object):
	def __init__(self):
		self.screen_size = (800,600)
		self.screen = pygame.display.set_mode(self.screen_size)

		self.clock = pygame.time.Clock()
		self.framerate = 60

		self.reset()
		self.run()

	def reset(self):
		self.world = World(self)

	def update(self):
		self.world.update()

	def move(self):
		self.world.move()

	def render(self):
		self.world.render()
		pygame.display.flip()

	def run(self):
		self.running = True
		while self.running:
			self.events = pygame.event.get()
			self.keys = list(pygame.key.get_pressed())
			self.mouse_pos = pygame.mouse.get_pos()
			self.time = time.time()

			self.update()
			self.move()
			self.render()

			for event in self.events:
				if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
					self.running = False

			self.clock.tick(self.framerate)
		pygame.quit()


# ====== PROGRAM START ======
main = Main()