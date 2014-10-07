import pygame
from pygame.locals import*

from Entity import Entity
from ..Sprite import *


class Baddie1(Entity):
	def init(self):
		self.sprite = Sprite(self.main, "imgs/sprites/baddie1", 2.0)
		self.sprite.set_frame("1")

		self.direction = 3

		self.anim = 0
		self.anim_length = 7

		self.hurt_length = 10
		self.hurt_delay = 0

		self.prev_pos = tuple(self.pos)
		self.health = 2
		self.vec = [0,0]

		self.is_bad = True

	def hurt_me(self):
		#TODO: Make hurt sound here.
		self.sprite.set_frame("1")

	def update(self):
		#we check to see which direction we'll be moving
		self.vec = [0,0]
		speed = 3.5

		self.anim += 1
		self.anim %= self.anim_length*2

		if self.hurt != 0:
			self.hurt += 1
			if self.is_hurt:
				if self.hurt >= self.hurt_length:
					self.is_hurt = False
			else:
				if self.hurt - self.hurt_length >= self.hurt_delay:
					self.hurt = 0

		if not self.is_hurt:
			self.sprite.set_frame(str(1 + int(self.anim/float(self.anim_length))))
		else:
			self.vec = tuple(self.hurt_direction)

	def move(self):
		#finally displaces the baddie
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

		if self.is_hurt:
			img = img.copy()
			img.fill((255,0,0), None, special_flags = BLEND_RGB_MULT)

		self.main.screen.blit(img, rect)
