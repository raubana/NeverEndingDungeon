import pygame
from pygame.locals import*

from common import lerp_colors, lerp
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

class FastFadeFromWhite(Fade):
	def init(self):
		self.fade_length = 15

	def render(self):
		s = pygame.Surface(self.main.screen_size,SRCALPHA)
		p = min(max((self.fade-self.pre_delay)/float(self.fade_length),0.0),1.0)
		color = (255,255,255,lerp(255,0,p))
		s.fill(color)
		self.main.screen.blit(s,(0,0))

class FadeToWhite(Fade):
	def render(self):
		s = pygame.Surface(self.main.screen_size,SRCALPHA)
		p = min(max((self.fade-self.pre_delay)/float(self.fade_length),0.0),1.0)
		color = (255,255,255,lerp(0,255,p))
		s.fill(color)
		self.main.screen.blit(s,(0,0))

class WhiteToBlack(Fade):
	def init(self):
		self.is_covering_screen = True

	def render(self):
		p = min(max((self.fade-self.pre_delay)/float(self.fade_length),0.0),1.0)
		color = lerp_colors((255,255,255),(0,0,0),p)
		self.main.screen.fill(color)



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


class Credits(object):
	def __init__(self, main):
		self.main = main
		self.dead = False

		self.fade = 0
		self.fade_length = 60
		self.fadeout_delay = 120

		self.is_covering_screen = True

		self.the_end = pygame.image.load("imgs/misc/theend.png")
		self.for_now = pygame.image.load("imgs/misc/fornow.png")

	def update(self):
		if not self.dead:
			self.fade += 1
			if self.fade > self.fade_length * 6 + self.fadeout_delay:
				self.dead = True

	def render(self):
		self.main.screen.fill((0,0,0))

		img1 = self.the_end.copy()
		img2 = self.for_now.copy()

		gap = (img1.get_height()+img2.get_height())*0.2

		center = (self.main.screen_size[0]/2, self.main.screen_size[1]/2)

		rect1 = img1.get_rect(midbottom = (center[0], center[1]-(gap/2)))
		rect2 = img1.get_rect(midtop = (center[0], center[1]+(gap/2)))

		fade = self.fade
		if fade < self.fade_length*2:
			p = min(fade / float(self.fade_length),1.0)
			img1.fill((255,255,255,int(255*p)),None,special_flags=BLEND_RGBA_MULT)
			self.main.screen.blit(img1, rect1)
		elif fade < self.fade_length*4 + self.fadeout_delay:
			p = min((fade-(self.fade_length*2)) / float(self.fade_length),1.0)
			img2.fill((255,255,255,int(255*p)),None,special_flags=BLEND_RGBA_MULT)
			self.main.screen.blit(img1, rect1)
			self.main.screen.blit(img2, rect2)
		elif fade < self.fade_length*5 + self.fadeout_delay:
			p = max(min((fade-(self.fade_length*4 + self.fadeout_delay)) / float(self.fade_length),1.0),0.0)
			img1.fill((255,255,255,int(255*(1-p))),None,special_flags=BLEND_RGBA_MULT)
			img2.fill((255,255,255,int(255*(1-p))),None,special_flags=BLEND_RGBA_MULT)
			self.main.screen.blit(img1, rect1)
			self.main.screen.blit(img2, rect2)


