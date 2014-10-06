import pygame
from pygame.locals import*

from Entity import Entity


class Player(Entity):
	"""
	This is the parent Player class.
	"""

	def init(self):
		self.prev_pos = tuple(self.pos)
		self.health = 100
		self.vec = [0,0]

	def update(self):
		#we check to see which direction we'll be moving
		self.vec = [0,0]
		speed = 3.5

		if self.main.keys[K_LEFT]:
			self.vec[0] -= speed
		if self.main.keys[K_RIGHT]:
			self.vec[0] += speed
		if self.main.keys[K_UP]:
			self.vec[1] -= speed
		if self.main.keys[K_DOWN]:
			self.vec[1] += speed

		#we normalize our vector
		length = ((self.vec[0]**2) + (self.vec[1]**2))**0.5
		if length > 0:
			self.vec[0] /= length
			self.vec[1] /= length
			self.vec[0] *= speed
			self.vec[1] *= speed

	def move(self):
		#finally displaces the player
		self.prev_pos = tuple(self.pos)
		self.pos[0] += self.vec[0]
		self.pos[1] += self.vec[1]

	def render(self):
		offset = self.main.world.visible_grid.offset
		pos = (self.pos[0]+offset[0], self.pos[1]+offset[1])
		pos = (int(pos[0]), int(pos[1]))
		pygame.draw.circle(self.main.screen, (255,255,255), pos, 16)