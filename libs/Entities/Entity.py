import pygame

from ..TileSystem import TILE_SIZE

class Entity(object):
	"""
	The parent class for all entities.
	"""
	def __init__(self, main, pos, size = (24,24)):
		self.main = main
		self.pos = pos
		self.size = size
		self.calc_rect()
		self.dead = False
		self.init()

	def init(self):
		"""
		It may seem silly, but this is here so that the child-class
		can do it's own initializing after the parent is done.
		"""
		pass

	def update(self):
		pass

	def move(self):
		pass

	def calc_rect(self):
		self.rect = pygame.Rect([self.pos[0]-(self.size[0]/2),
								 self.pos[1]-(self.size[1]/2),
								 self.size[0],
								 self.size[1]])

	def do_tile_collision_detection(self):
		offset = [0,0]
		for x in xrange(int(self.rect.left/TILE_SIZE),int(self.rect.right/TILE_SIZE)+1):
			for y in xrange(int(self.rect.top/TILE_SIZE),int(self.rect.bottom/TILE_SIZE)+1):
				if self.main.world.grid.is_legal_coords((x,y)) and self.main.world.grid.tiles[y][x].solid:
					rect = pygame.Rect([x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE])
					left = rect.right - self.rect.left
					top = rect.bottom - self.rect.top
					right = self.rect.right - rect.left
					bottom = self.rect.bottom - rect.top

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
		if offset[0] != 0 or offset[1] != 0:
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.calc_rect()

	def flag_for_rerender(self):
		self.flagged_for_rerender = True

	def rerender(self):
		pass

	def render(self):
		pass

