
import os

class Sprite(object):
	def __init__(self, main, folder, directional = True):
		self.main = main

		self.sprites = {}
		self.directional = directional

		files = os.listdir(folder)
		for f in files:
			i = f.rfind(".")
			if i != -1:
				name = f[:i]
			else:
				name = f