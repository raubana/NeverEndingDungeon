import pygame
from pygame.locals import *

class Drop(object):
	def __init__(self, main, pos, size = (16,16)):
		self.main = main
		self.pos = list(pos)
		self.size = size
		self.calc_rect()
		self.dead = False

		self.will_disappear = True
		self.life = 300
		self.pre_disappear_life = 120

		self.img = pygame.Surface((1,1))

		self.init()

	def init(self):
		pass

	def update(self):
		if self.will_disappear:
			self.life -= 1
			if self.life <= 0:
				self.dead = True

	def move(self):
		pass

	def calc_rect(self):
		self.rect = pygame.Rect([self.pos[0]-(self.size[0]/2),
								 self.pos[1]-(self.size[1]/2),
								 self.size[0],
								 self.size[1]])

	def render(self):
		if not self.dead:
			offset = self.main.world.visible_grid.offset
			pos = (self.rect.centerx+offset[0], self.rect.centery+offset[1])
			pos = (int(pos[0]), int(pos[1]))
			img = self.img.copy()
			rect = img.get_rect(center = pos)
			if self.will_disappear:
				if self.life <= self.pre_disappear_life:
					dif = self.pre_disappear_life - self.life
					img = img.copy()
					if dif%2 == 0:
						img.fill((255,255,255,192), None, special_flags = BLEND_RGBA_MULT)
					else:
						img.fill((255,255,255,64), None, special_flags = BLEND_RGBA_MULT)
			self.main.screen.blit(img, rect)