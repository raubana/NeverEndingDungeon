import pygame
from pygame.locals import*

from common import lerp_colors


class Fade(object):
	def __init__(self, main):
		self.main = main
		self.is_covering_screen = False

		self.fade = 0
		self.fade_length = 90

		self.dead = False

		self.init()

	def init(self):
		pass

	def update(self):
		if not self.dead :
			self.fade += 1
			if self.fade > self.fade_length + 1:
				self.dead = True

	def render(self):
		pass


class FadeFromBlack(Fade):
	def render(self):
		p = min(max(self.fade/float(self.fade_length),0.0),1.0)
		color = lerp_colors((0,0,0),(255,255,255),p)
		self.main.screen.fill(color,None,special_flags=BLEND_RGB_MULT)