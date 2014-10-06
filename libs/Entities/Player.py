import pygame
from pygame.locals import*

from Entity import Entity
from ..Sprite import *


class Player(Entity):
	"""
	This is the parent Player class.
	"""

	def init(self):
		self.sprite = Sprite(self.main, "imgs/sprites/player", 2.0)
		self.sprite.set_frame("walk1")
		self.direction = 3
		self.walk = 0
		self.walk_length = 15
		self.walking = False
		self.prev_pos = tuple(self.pos)
		self.health = 100
		self.vec = [0,0]

	def update(self):
		#we check to see which direction we'll be moving
		self.vec = [0,0]
		speed = 3.5

		for e in self.main.events:
			if e.type in (KEYDOWN,KEYUP) and e.key in (K_LEFT,K_UP,K_RIGHT,K_DOWN):
				if e.type == KEYDOWN:
					if e.key == K_LEFT: self.direction = 0
					elif e.key == K_UP: self.direction = 1
					elif e.key == K_RIGHT: self.direction = 2
					elif e.key == K_DOWN: self.direction = 3
					self.walking = True
				elif e.type == KEYUP:
					done_walking = True
					if e.key == K_LEFT and self.direction == 0:
						self.main.keys[K_LEFT] = False
					elif e.key == K_UP and self.direction == 1:
						self.main.keys[K_UP] = False
					elif e.key == K_RIGHT and self.direction == 2:
						self.main.keys[K_RIGHT] = False
					elif e.key == K_DOWN and self.direction == 3:
						self.main.keys[K_DOWN] = False
					else:
						done_walking = False
					if done_walking:
						#we also check if there's a key still being pressed, but only one
						count = int(self.main.keys[K_LEFT]) + int(self.main.keys[K_UP]) + int(self.main.keys[K_RIGHT]) + int(self.main.keys[K_DOWN])
						if count == 1:
							if self.main.keys[K_LEFT]: self.direction = 0
							elif self.main.keys[K_UP]: self.direction = 1
							elif self.main.keys[K_RIGHT]: self.direction = 2
							elif self.main.keys[K_DOWN]: self.direction = 3
							else:
								self.walking = False
						else:
							self.walking = False

		if self.walking:
			if self.direction == 0: self.vec[0] -= speed
			elif self.direction == 2: self.vec[0] += speed
			elif self.direction == 1: self.vec[1] -= speed
			elif self.direction == 3: self.vec[1] += speed

		#we normalize our vector
		length = ((self.vec[0]**2) + (self.vec[1]**2))**0.5
		if length > 0:
			self.vec[0] /= length
			self.vec[1] /= length
			self.vec[0] *= speed
			self.vec[1] *= speed

			self.walk += length
			self.walk %= self.walk_length*2

			if self.direction == 0: direction = DIRECTION_LEFT
			elif self.direction == 1: direction = DIRECTION_UP
			elif self.direction == 2: direction = DIRECTION_RIGHT
			else: direction = DIRECTION_DOWN

			self.sprite.direction = direction

			self.sprite.set_frame("walk" + str(1 + int(self.walk/float(self.walk_length))))

	def move(self):
		#finally displaces the player
		self.prev_pos = tuple(self.pos)
		self.pos[0] += self.vec[0]
		self.pos[1] += self.vec[1]
		self.calc_rect()
		self.do_tile_collision_detection()

	def render(self):
		offset = self.main.world.visible_grid.offset
		pos = (self.pos[0]+offset[0], self.pos[1]+offset[1])
		pos = (int(pos[0]), int(pos[1]))
		img = self.sprite.get_img()
		rect = img.get_rect(center = pos)
		self.main.screen.blit(img, rect)