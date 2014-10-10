import pygame
from pygame.locals import*

from common import lerp_colors
from libs.Sprite import Sprite


class Fade(object):
	def __init__(self, main):
		self.main = main
		self.is_covering_screen = False

		self.fade = 0
		self.pre_delay = 0
		self.fade_length = 120

		self.dead = False

		self.init()

	def init(self):
		pass

	def update(self):
		if not self.dead :
			self.fade += 1
			if self.fade > self.fade_length + self.pre_delay + 1:
				self.dead = True

	def render(self):
		pass


class FadeFromBlack(Fade):
	def render(self):
		p = min(max((self.fade-self.pre_delay)/float(self.fade_length),0.0),1.0)
		color = lerp_colors((0,0,0),(255,255,255),p)
		self.main.screen.fill(color,None,special_flags=BLEND_RGB_MULT)

class FadeToBlack(Fade):
	def render(self):
		p = min(max((self.fade-self.pre_delay)/float(self.fade_length),0.0),1.0)
		color = lerp_colors((255,255,255),(0,0,0),p)
		self.main.screen.fill(color,None,special_flags=BLEND_RGB_MULT)

class FadeToBlackOnDeath(Fade):
	def init(self):
		self.pre_delay = 220
		self.fade_length = 30

	def render(self):
		p = min(max((self.fade-self.pre_delay)/float(self.fade_length),0.0),1.0)
		color = lerp_colors((255,255,255),(0,0,0),p)
		self.main.screen.fill(color,None,special_flags=BLEND_RGB_MULT)

class IntroFadeSequence(object):
	def __init__(self, main):
		self.main = main
		self.dead = False

		self.stage = -1
		self.fade = 0

		self.intro_delay = 120
		self.fadein_length = 60
		self.hold_length = 180
		self.fadeout_length = 60
		self.end_delay = 120

		self.is_covering_screen = True

		self.sprite = Sprite(self.main, "imgs/sprites/raubana", 3, False)

	def update(self):
		if not self.dead:
			if self.stage == -1:
				self.fade += 1
				if self.fade >= self.intro_delay:
					self.fade = 0
					self.stage = 0
			elif self.stage < 2:
				if self.stage == 0:
					self.sprite.set_frame("raubana")
				elif self.stage == 1:
					self.sprite.set_frame("pyweek")

				self.fade += 1
				if self.fade >= self.fadein_length + self.hold_length + self.fadeout_length:
					self.fade = 0
					self.stage += 1
			else:
				self.fade += 1
				if self.fade >= self.end_delay:
					self.dead = True

	def render(self):
		self.main.screen.fill((0,0,0))
		if self.stage >= 0 and self.stage <= 1:
			img = self.sprite.get_img()
			rect = img.get_rect(center = (self.main.screen_size[0]/2, self.main.screen_size[1]/2))

			fade = self.fade
			if fade < self.fadein_length:
				img = img.copy()
				p = fade / float(self.fadein_length)
				img.fill((255,255,255,int(255*p)),None,special_flags=BLEND_RGBA_MULT)
			elif fade >= self.fadein_length + self.hold_length:
				img = img.copy()
				p = min((fade-self.fadein_length-self.hold_length) / float(self.fadein_length),1.0)
				img.fill((255,255,255,int(255*(1-p))),None,special_flags=BLEND_RGBA_MULT)

			self.main.screen.blit(img, rect)


