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
		self.sword_sprite = Sprite(self.main, "imgs/sprites/player_sword", 2.0)

		self.direction = 3
		self.walk = 0
		self.walk_length = 15
		self.walking = False
		self.attacking = False
		self.attack = 0
		self.attack_length = 10
		self.attack_delay = 5
		self.prev_pos = tuple(self.pos)
		self.health = 100
		self.vec = [0,0]

	def update(self):
		#we check to see which direction we'll be moving
		self.vec = [0,0]
		speed = 3.5

		update_walk_sprite = False

		if self.attack != 0:
			self.attack += 1
			if self.attacking:
				if self.attack >= self.attack_length:
					self.attacking = False
					update_walk_sprite = True
			else:
				if self.attack - self.attack_length >= self.attack_delay:
					self.attack = 0

		for e in self.main.events:
			if not self.attacking:
				if e.type in (KEYDOWN,KEYUP) and e.key in (K_a,K_w,K_d,K_s):
					if e.type == KEYDOWN:
						if e.key == K_a:
							self.direction = 0
							self.main.keys[K_a] = True
						elif e.key == K_w:
							self.direction = 1
							self.main.keys[K_w] = True
						elif e.key == K_d:
							self.direction = 2
							self.main.keys[K_d] = True
						elif e.key == K_s:
							self.direction = 3
							self.main.keys[K_s] = True
						self.walking = True

		if self.walking:
			done_walking = True
			if not self.main.keys[K_a] and self.direction == 0:
				pass
			elif not self.main.keys[K_w] and self.direction == 1:
				pass
			elif not self.main.keys[K_d] and self.direction == 2:
				pass
			elif not self.main.keys[K_s] and self.direction == 3:
				pass
			else:
				done_walking = False
			if done_walking:
				#we also check if there's a key still being pressed, but only one
				count = int(self.main.keys[K_a]) + int(self.main.keys[K_w]) + int(self.main.keys[K_d]) + int(self.main.keys[K_s])
				if count == 1:
					if self.main.keys[K_a]: self.direction = 0
					elif self.main.keys[K_w]: self.direction = 1
					elif self.main.keys[K_d]: self.direction = 2
					elif self.main.keys[K_s]: self.direction = 3
					else:
						self.walking = False
				else:
					self.walking = False

		if not self.attacking:
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

				update_walk_sprite = True

		for e in self.main.events:
			if e.type == KEYDOWN and e.key == K_RETURN:
				if not self.attacking and self.attack == 0:
					#TODO: Do attack sound
					#TODO: Check if there's anything the player just hit.
					self.attacking = True
					self.attack = 1
					self.sprite.set_frame("jab")
					if self.direction == 0: self.sword_sprite.direction = DIRECTION_LEFT
					elif self.direction == 1: self.sword_sprite.direction = DIRECTION_UP
					elif self.direction == 2: self.sword_sprite.direction = DIRECTION_RIGHT
					else: self.sword_sprite.direction = DIRECTION_DOWN
					self.sword_sprite.set_frame("")

		if update_walk_sprite:
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

		if self.attacking:
			sword_img = self.sword_sprite.get_img()
			if self.direction == 0:
				sword_rect = sword_img.get_rect(midright = (pos[0]-12,pos[1]))
			elif self.direction == 1:
				sword_rect = sword_img.get_rect(midbottom = (pos[0],pos[1]-12))
			elif self.direction == 2:
				sword_rect = sword_img.get_rect(midleft = (pos[0]+12,pos[1]))
			elif self.direction == 3:
				sword_rect = sword_img.get_rect(midtop = (pos[0],pos[1]+12))
			if self.direction == 1:
				self.main.screen.blit(sword_img, sword_rect)
				self.main.screen.blit(img, rect)
			else:
				self.main.screen.blit(img, rect)
				self.main.screen.blit(sword_img, sword_rect)
		else:
			self.main.screen.blit(img, rect)