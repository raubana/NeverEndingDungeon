# ====== IMPORTS ======
# --- Pygame ---
import pygame
from pygame.locals import*
pygame.init()

# --- Custom Modules ---
from libs.World import World

# --- Misc. ---
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
		"""
		RESET: Called when the entire application needs to be reset.
		"""
		self.world = World(self)

	def update(self):
		"""
		UPDATE: Called to perform logic calculations. Called before any movements are performed.
		"""
		self.world.update()

	def move(self):
		"""
		MOVE: Called to perform logic calculations. Called after 'update'.
		"""
		self.world.move()

	def render(self):
		"""
		RENDER: Called after 'update' and 'move' are done,
		so that any changes can be rendered and then displayed on screen.
		"""
		#self.screen.fill((0,0,0)) #We only use this when necessary.
		self.world.render()
		pygame.display.flip()

	def run(self):
		self.running = True
		while self.running:
			self.events = pygame.event.get()
			self.keys = pygame.key.get_pressed()
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