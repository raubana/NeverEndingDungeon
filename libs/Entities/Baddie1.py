import pygame
from pygame.locals import*

from Entity import Entity
from ..Sprite import *
from ..TileSystem import TILE_SIZE, round_coords
from ..common import lerp_pos


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

		self.path_update_length = 60
		self.path_update = int(self.path_update_length)-2
		self.target_pos = None
		self.path = []

		self.is_bad = True

	def hurt_me(self):
		self.sprite.set_frame("1")
		self.path_update = int(self.path_update_length)
		if self.dead:
			self.main.world.play_sound("enemy_death", self.pos)
		else:
			self.main.world.play_sound("enemy_hurt", self.pos)

	def fall_me(self):
		self.main.world.play_sound("falling", self.pos)

	def update(self):
		#we check to see which direction we'll be moving
		self.vec = [0,0]
		speed = 1.5

		self.coords = round_coords((float(self.pos[0])/TILE_SIZE, float(self.pos[1])/TILE_SIZE))

		if not self.dead and not self.falling:
			#Animation Update
			self.anim += 1
			self.anim %= self.anim_length*2

			#Hurt Update
			if self.hurt != 0:
				self.hurt += 1
				if self.is_hurt:
					if self.hurt >= self.hurt_length:
						self.is_hurt = False
				else:
					if self.hurt - self.hurt_length >= self.hurt_delay:
						self.hurt = 0

			#Hurt/Animation
			if not self.is_hurt:
				self.sprite.set_frame(str(1 + int(self.anim/float(self.anim_length))))
			else:
				self.vec = tuple(self.hurt_direction)

			#Pit Detection
			pos = (float(self.pos[0])/TILE_SIZE, float(self.pos[1])/TILE_SIZE)
			if not self.main.world.grid.is_legal_coords(pos):
				self.__fall__()

			if not self.is_hurt:
				#Path Following
				if self.target_pos != None:
					dif = (self.target_pos[0]-self.pos[0],self.target_pos[1]-self.pos[1])
					if abs(dif[0]) > abs(dif[1]):
						if dif[0] > 0:
							self.direction = 2
							self.vec = [speed,0]
						else:
							self.direction = 0
							self.vec = [-speed,0]
					else:
						if dif[1] > 0:
							self.direction = 3
							self.vec = [0, speed]
						else:
							self.direction = 1
							self.vec = [0, -speed]
					self.set_sprite_direction()
					#Check if we've reached this pos or if this target position is bad.
					mx = abs(dif[0])
					my = abs(dif[1])
					m = max(mx, my)
					if m <= speed*2 or m >= TILE_SIZE*1.5 or (mx > TILE_SIZE*0.5 and my > TILE_SIZE*0.5):
						self.target_pos = None
					else:
						pos = (float(self.target_pos[0])/TILE_SIZE, float(self.target_pos[1])/TILE_SIZE)
						pos = round_coords(pos)
						if not self.main.world.grid.is_legal_coords(pos):
							self.target_pos = None
						else:
							tile = self.main.world.grid.tiles[int(pos[1])][int(pos[0])]
							if tile.solid:
								self.target_pos = None
				else:
					if len(self.path) > 0:
						self.target_pos = self.path.pop(0)
						#we check if this position is bad, in which case we discard our path.
						pos = (float(self.target_pos[0])/TILE_SIZE, float(self.target_pos[1])/TILE_SIZE)
						if not self.main.world.grid.is_legal_coords(pos):
							self.target_pos = None
						if self.target_pos == None:
							self.path = []
						if len(self.path) == 0:
							self.path_update = int(self.path_update_length/2)

				#Path Update
				self.path_update += 1
				if self.path_update >= self.path_update_length:
					self.path_update = 0
					if self.target_pos != None:
						pos = round_coords((float(self.target_pos[0])/TILE_SIZE, float(self.target_pos[1])/TILE_SIZE))
					else:
						pos = self.coords
					self.path = self.main.world.grid.get_path(pos,
									(self.main.world.player.pos[0]/TILE_SIZE, self.main.world.player.pos[1]/TILE_SIZE))
		else:
			#Update Fall
			if self.fall != 0:
				if self.fall < self.fall_length:
					self.fall += 1
					self.direction = (self.fall/4)%4
					self.set_sprite_direction()
					self.sprite.set_frame("1")
					pos = round_coords((float(self.pos[0])/TILE_SIZE,float(self.pos[1])/TILE_SIZE))
					pos = [(pos[0]+0.5)*TILE_SIZE, (pos[1]+0.5)*TILE_SIZE]
					self.pos = lerp_pos(self.pos,
										pos,
										0.1)
				else:
					self.dead = True
					self.falling = False

	def move(self):
		#finally displaces the baddie
		self.prev_pos = tuple(self.pos)
		self.pos[0] += self.vec[0]
		self.pos[1] += self.vec[1]
		self.calc_rect()
		if not self.dead:
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
		elif self.falling:
			img = img.copy()
			x = int(255*((self.fall_length-self.fall)/float(self.fall_length)))
			img.fill((255,255,255,x), None, special_flags = BLEND_RGBA_MULT)

		self.main.screen.blit(img, rect)
