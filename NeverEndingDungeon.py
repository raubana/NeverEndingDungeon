import pygame
from pygame.locals import*
from libs.MusicMan import MusicMan

pygame.mixer.pre_init(frequency = 44010, buffer = 2**9)
pygame.init()

pygame.mixer.set_num_channels(100)
pygame.mixer.set_reserved(1)

from libs.World import World

import time, random


# ====== CLASSES ======
class Main(object):
	def __init__(self):
		self.screen_size = (800,600)
		self.screen = pygame.display.set_mode(self.screen_size)

		pygame.display.set_caption("The Never Ending Dungeon", "NED")

		self.clock = pygame.time.Clock()
		self.framerate = 60

		self.reset()
		self.run()

	def reset(self):
		self.world = World(self)
		self.music = MusicMan(self)

	def update(self):
		self.world.update()
		self.music.update()

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
				if event.type == QUIT:
					self.running = False

			self.clock.tick(self.framerate)
		pygame.quit()


# ====== PROGRAM START ======
main = Main()