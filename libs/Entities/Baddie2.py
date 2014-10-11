import pygame
from pygame.locals import*

from Entity import Entity
from ..Sprite import *
from ..TileSystem import TILE_SIZE, round_coords
from ..common import lerp_pos

from Baddie1 import Baddie1


class Baddie2(Baddie1):
	def init(self):
		self.sprite = Sprite(self.main, "imgs/sprites/baddie2", 2.0)
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

		self.speed = 3
		self.shit_path_freq = 1.0
