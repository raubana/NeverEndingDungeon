import pygame

import os

DIRECTION_UP = "back"
DIRECTION_DOWN = "front"
DIRECTION_LEFT = "left"
DIRECTION_RIGHT = "right"

class Sprite(object):
	def __init__(self, main, folder, scale, directional = True):
		self.main = main

		self.frames = {}
		self.directional = directional

		self.current_frame = pygame.Surface((1,1))
		self.direction = DIRECTION_DOWN

		files = os.listdir(folder)
		for f in files:
			i = f.rfind(".")
			if i != -1:
				name = f[:i]
			else:
				name = f
			img = pygame.image.load(folder+"/"+f)
			if scale != 1.0:
				size = (int(img.get_width()*scale), int(img.get_height()*scale))
				img = pygame.transform.scale(img, size)
			self.frames[name] = img

	def set_frame(self, frame):
		name = str(frame)
		if self.directional:
			name = self.direction + "_" + name
		if name in self.frames:
			self.current_frame = self.frames[name]

	def get_img(self):
		return self.current_frame