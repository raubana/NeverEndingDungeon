import pygame
from pygame.locals import*

from Entity import Entity
from ..Sprite import *
from ..TileSystem import TILE_SIZE, round_coords
from ..common import lerp_pos


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
		self.attack_delay = 14

		self.is_hurt = False
		self.hurt = 0
		self.hurt_length = 10
		self.hurt_delay = 45
		self.hurt_direction = [0,0]

		self.dying = 0
		self.dying_predelay = 60
		self.dying_length = 120

		self.prev_pos = tuple(self.pos)
		self.health = 8
		self.vec = [0,0]

	def hurt_me(self):
		self.attacking = False
		self.attack = 0
		self.sprite.set_frame("1")
		if self.dead:
			self.hurt = 0
			self.is_hurt = False
			self.is_dying = True
			self.dying = 1

	def update(self):
		#we check to see which direction we'll be moving
		if not self.dead and not self.falling:
			self.vec = [0,0]
			speed = 3.0

			update_walk_sprite = False

			#Baddie Collision Detection
			for npc in self.main.world.npcs:
				if npc.is_bad and not npc.dead and not npc.is_hurt:
					offset = [0,0]
					if self.rect.colliderect(npc.rect):
						dif = (npc.rect.left - self.rect.left, npc.rect.top - self.rect.top)
						if pygame.mask.from_surface(self.sprite.get_img()).overlap(pygame.mask.from_surface(npc.sprite.get_img()), dif):
							left = npc.rect.right - self.rect.left
							top = npc.rect.bottom - self.rect.top
							right = self.rect.right - npc.rect.left
							bottom = self.rect.bottom - npc.rect.top

							m = min(left,top,right,bottom)
							if m > 0:
								if left == m:
									if abs(offset[0]) < left: offset[0] = left
								elif top == m:
									if abs(offset[1]) < top: offset[1] = top
								elif right == m:
									if abs(offset[0]) < right: offset[0] = -right
								elif bottom == m:
									if abs(offset[1]) < bottom: offset[1] = -bottom
								if abs(offset[0]) > abs(offset[1]):
									if offset[0] > 0:
										offset = [1,0]
									else:
										offset = [-1,0]
								else:
									if offset[1] > 0:
										offset = [0,1]
									else:
										offset = [0,-1]
								offset[0] *= 3
								offset[1] *= 3
								self.__hurt__(1,offset)

			#Pit Detection
			pos = (float(self.pos[0])/TILE_SIZE, float(self.pos[1])/TILE_SIZE)
			if not self.main.world.grid.is_legal_coords(pos):
				self.__fall__()

			#Hurt Update
			if self.hurt != 0:
				self.hurt += 1
				if self.is_hurt:
					if self.hurt >= self.hurt_length:
						self.is_hurt = False
						update_walk_sprite = True
				else:
					if self.hurt - self.hurt_length >= self.hurt_delay:
						self.hurt = 0

			if not self.is_hurt:
				#Attack Update
				if self.attack != 0:
					self.attack += 1
					if self.attacking:
						if self.attack >= self.attack_length:
							self.attacking = False
							update_walk_sprite = True
						else:
							self.detect_sword_collisions()
					else:
						if self.attack - self.attack_length >= self.attack_delay:
							self.attack = 0

				#Directional Control
				for e in self.main.events:
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

				#Motion
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

						self.set_sprite_direction()

						update_walk_sprite = True

				#Attacking
				for e in self.main.events:
					if e.type == KEYDOWN and e.key == K_RETURN:
						if not self.attacking and self.attack == 0:
							#TODO: Do attack sound
							self.attacking = True
							self.attack = 1
							self.sprite.set_frame("jab")
							if self.direction == 0: self.sword_sprite.direction = DIRECTION_LEFT
							elif self.direction == 1: self.sword_sprite.direction = DIRECTION_UP
							elif self.direction == 2: self.sword_sprite.direction = DIRECTION_RIGHT
							else: self.sword_sprite.direction = DIRECTION_DOWN
							self.sword_sprite.set_frame("")
							self.detect_sword_collisions()
			else:
				self.vec = tuple(self.hurt_direction)

			if update_walk_sprite:
				self.sprite.set_frame("walk" + str(1 + int(self.walk/float(self.walk_length))))
		else:
			#Update Death
			self.vec = (0,0)
			if self.dying != 0:
				self.dying += 1
				if self.dying < self.dying_predelay:
					pass
				elif self.dying - self.dying_predelay >= self.dying_length:
					self.dying = 0
					self.is_dying = False
				else:
					self.is_hurt = False
					self.direction = (self.dying/4)%4
					self.set_sprite_direction()
					self.sprite.set_frame("walk1")

			#Update Fall
			if self.fall != 0:
				self.fall += 1
				if self.fall < self.dying_predelay:
					pass
				elif self.fall - self.dying_predelay < self.fall_length:
					self.direction = ((self.fall-self.dying_predelay)/4)%4
					self.set_sprite_direction()
					self.sprite.set_frame("walk1")
					pos = round_coords((float(self.pos[0])/TILE_SIZE,float(self.pos[1])/TILE_SIZE))
					pos = [(pos[0]+0.5)*TILE_SIZE, (pos[1]+0.5)*TILE_SIZE]
					self.pos = lerp_pos(self.pos,
										pos,
										0.1)
				else:
					self.dead = True
					self.falling = False

	def detect_sword_collisions(self):
		#Sword Attack Collision Detection
		sword_rect = self.get_sword_rect()
		for npc in self.main.world.npcs:
			if npc.is_bad and not npc.dead:
				if sword_rect.colliderect(npc.rect):
					dif = (npc.rect.left - sword_rect.left, npc.rect.top - sword_rect.top)
					if pygame.mask.from_surface(self.sword_sprite.get_img()).overlap(pygame.mask.from_surface(npc.sprite.get_img()), dif):
						offset = [0,0]
						if self.direction == 0:
							offset = [-1,0]
						elif self.direction == 2:
							offset = [1,0]
						elif self.direction == 1:
							offset = [0,-1]
						else:
							offset = [0,1]
						offset[0] *= 5
						offset[1] *= 5
						npc.__hurt__(1,offset)

	def calc_rect(self):
		self.rect = pygame.Rect([self.pos[0]-(self.size[0]/2),
								 self.pos[1]-int(self.size[1]*0.75),
								 self.size[0],
								 self.size[1]])

	def move(self):
		#finally displaces the player
		self.prev_pos = tuple(self.pos)
		self.pos[0] += self.vec[0]
		self.pos[1] += self.vec[1]
		self.calc_rect()
		if not self.dead:
			self.do_tile_collision_detection()

	def get_sword_rect(self):
		sword_img = self.sword_sprite.get_img()
		if self.sword_sprite.direction == DIRECTION_LEFT:
			sword_rect = sword_img.get_rect(midright = (self.rect.centerx-12,self.rect.centery))
		elif self.sword_sprite.direction == DIRECTION_UP:
			sword_rect = sword_img.get_rect(midbottom = (self.rect.centerx,self.rect.centery-12))
		elif self.sword_sprite.direction == DIRECTION_RIGHT:
			sword_rect = sword_img.get_rect(midleft = (self.rect.centerx+12,self.rect.centery))
		elif self.sword_sprite.direction == DIRECTION_DOWN:
			sword_rect = sword_img.get_rect(midtop = (self.rect.centerx,self.rect.centery+12))
		return sword_rect

	def render(self):
		if not self.dead or self.dying or self.falling:
			order = 0

			offset = self.main.world.visible_grid.offset
			pos = (self.rect.centerx+offset[0], self.rect.centery+offset[1])
			pos = (int(pos[0]), int(pos[1]))
			img = self.sprite.get_img()
			rect = img.get_rect(center = pos)
			filter = 0
			sword_rect = None
			sword_img = None

			if self.is_hurt:
				img = img.copy()
				img.fill((255,0,0), None, special_flags = BLEND_RGB_MULT)
			elif self.hurt != 0:
				img = img.copy()
				if self.hurt%2 == 0:
					img.fill((255,255,255,192), None, special_flags = BLEND_RGBA_MULT)
				else:
					img.fill((255,255,255,64), None, special_flags = BLEND_RGBA_MULT)
			elif self.falling and self.fall >= self.dying_predelay:
				img = img.copy()
				x = int(255*((self.fall_length-(self.fall-self.dying_predelay))/float(self.fall_length)))
				img.fill((255,255,255,x), None, special_flags = BLEND_RGBA_MULT)

			if self.attacking:
				sword_img = self.sword_sprite.get_img()
				sword_rect = self.get_sword_rect().move(offset[0], offset[1])
				if self.sword_sprite.direction == DIRECTION_UP:
					order = 1
				else:
					order = 0

			if order == 0:
				if img != None:
					self.main.screen.blit(img, rect, special_flags=filter)
				if sword_img != None:
					self.main.screen.blit(sword_img, sword_rect)
			else:
				if sword_img != None:
					self.main.screen.blit(sword_img, sword_rect)
				if img != None:
					self.main.screen.blit(img, rect, special_flags=filter)