import pygame

from Drop import Drop
from libs.Sprite import Sprite

class Heart(Drop):
	def init(self):
		self.img = pygame.image.load("imgs/drops/heart.png")