# ====== IMPORTS ======
# --- Pygame ---
import pygame

# --- Misc. ---
import random

# ====== CONSTANTS ======
TILE_SIZE = 48  # The 2D size of a side of a single tile in pixels.


# ====== FUNCTIONS ======
def offset_to_coords(offset):
	"""This is for converting a VisibleGrid's offset to coordinates,
	which tell us which tile is in the top-left corner."""
	return (-int(offset[0]/TILE_SIZE), -int(offset[1]/TILE_SIZE))


# ====== CLASSES ======
class Grid(object):
	"""
	This class contains the tiles of the entire world.
	"""
	def __init__(self, main):
		self.main = main

		self.gridsize = (0,0) # in tiles.
		self.tiles = []

	def is_legal_coords(self, coords):
		"""
		Checks if the given coordinates are within the world
		(specifically meaning if a tile exists at that exact location).
		"""
		#first we check if this coord is within the bounds of the grid.
		if coords[0] < 0 or coords[1] < 0 or coords[0] >= self.gridsize[0] or coords[1] >= self.gridsize[1]:
			return False
		#next we check if there's a tile at this location.
		return self.tiles[coords[1]][coords[0]] != None


class Tile(object):
	def __init__(self, main):
		self.main = main
		self.solid = False
		self.deadly = False
		self.flagged_for_rerender = True
		self.rendered_surface = pygame.Surface((TILE_SIZE,TILE_SIZE))
		self.init()

	def init(self):
		pass

	def flag_for_rerender(self):
		self.flagged_for_rerender = True

	def rerender(self):
		if self.flagged_for_rerender:
			self.flagged_for_rerender = False
			color = (92+random.randint(-4,4),150+random.randint(-4,4),153+random.randint(-4,4))
			self.rendered_surface.fill(color)
			pygame.draw.rect(self.rendered_surface, (color[0]-10, color[1]-10, color[2]-10), (0,0,TILE_SIZE,TILE_SIZE), 1)

	def render(self, surface, pos, force = False):
		self.rerender()
		surface.blit(self.rendered_surface, pos)


class WallTile(Tile):
	def init(self):
		self.solid = True

	def rerender(self):
		if self.flagged_for_rerender:
			self.flagged_for_rerender = False
			color = (120,120,80)
			self.rendered_surface.fill(color)
			pygame.draw.rect(self.rendered_surface, (color[0]/2, color[1]/2, color[2]/2), (0,0,TILE_SIZE,TILE_SIZE), 1)



class VisibleGrid(object):
	"""
	This is the class that handles the 'side-scrolling' rendering.
	It will handle generating and rendering of the background by way
	of tiles.

	Visible offset is created when blitting this classes rendered surface
	to the screen.
	"""

	def __init__(self, main):
		self.main = main

		self.gridsize = self.calc_gridsize()
		self.rendered_surface = pygame.Surface((self.gridsize[0]*TILE_SIZE, self.gridsize[1]*TILE_SIZE))

		self.flagged_for_rerender = True  # Only True when the rendered_surface needs to be completely redone.
		#For example, when the offset changes enough that an entire new row or column becomes visible.

		self.offset = (0, 0)  # in pixels, this is relative to the screen.
		self.prev_offset = (0, 0) # this is for checking if we can reuse some of the data from the surface.

		self.coords = (0, 0) # in tiles, relative to the origin of the actual grid.
		self.prev_coords = (0, 0)

	def calc_gridsize(self):
		return (self.main.screen_size[0] / TILE_SIZE + 2, self.main.screen_size[1] / TILE_SIZE + 2)

	def set_offset(self, offset):
		offset = (int(offset[0]),int(offset[1]))
		if offset != self.offset:
			self.offset = offset
			new_coords = offset_to_coords(offset)
			if new_coords != self.coords:
				if new_coords == self.prev_coords:
					self.unflag_for_rerender()
				else:
					self.flag_for_rerender()
				self.coords = tuple(new_coords)

	def flag_for_rerender(self):
		# This can be called by anything, and will usually be called when:
		# 1. A visible tile changes in appearance.
		# 2. The offset becomes great enough that an entire new row or column becomes visible.
		self.flagged_for_rerender = True

	def unflag_for_rerender(self):
		self.flagged_for_rerender = False

	def rerender(self):
		"""
		RERENDER SHOULD NEVER BE CALLED OUTSIDE OF THIS CLASS.
		Rerendering is not the same as Rendering. Rerendering fixes problems with the pre-rendered surface that is
		then rendered to the screen. However, calling "rerender" does not directly affect the screen.
		"""
		if self.flagged_for_rerender:
			self.flagged_for_rerender = False

			coord_dif = (self.coords[0]-self.prev_coords[0], self.coords[1]-self.prev_coords[1])

			#first we try to reuse some of the old stuff again.
			if (coord_dif[0] != 0 or coord_dif[1] != 0) and abs(coord_dif[0]) < self.gridsize[0] and abs(coord_dif[1]) < self.gridsize[1]:
				self.rendered_surface.blit(self.rendered_surface,(-coord_dif[0]*TILE_SIZE, -coord_dif[1]*TILE_SIZE))

			# next we check for any tiles that need to be rendered to the surface,
			# including those that may have simply changed their appearance.
			for x in xrange(self.gridsize[0]):
				for y in xrange(self.gridsize[1]):
					is_new_tile = False
					is_new_tile = is_new_tile or (coord_dif[0] < 0 and x < -coord_dif[0])
					is_new_tile = is_new_tile or (coord_dif[1] < 0 and y < -coord_dif[1])
					is_new_tile = is_new_tile or (coord_dif[0] > 0 and x >= self.gridsize[0]-coord_dif[0])
					is_new_tile = is_new_tile or (coord_dif[1] > 0 and y >= self.gridsize[1]-coord_dif[1])

					pos = (x+self.coords[0]-1,y+self.coords[1]-1)
					if self.main.world.grid.is_legal_coords(pos):
						tile = self.main.world.grid.tiles[pos[1]][pos[0]]
					else:
						tile = None

					if (tile != None and (tile.flagged_for_rerender or is_new_tile)) or (tile == None and is_new_tile):
						if tile:
							# We tell the tile to render to the surface.
							tile.render(self.rendered_surface, (x*TILE_SIZE,y*TILE_SIZE))
						else:
							self.rendered_surface.fill((random.randint(0,32),random.randint(0,32),random.randint(0,32)),(x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))

	def render(self):
		"""
		Render is only called by world or main.
		"""
		self.rerender() #In case the pre-rendered surface needs to be changed.
		offset = (int(self.offset[0]%TILE_SIZE)-TILE_SIZE, int(self.offset[1]%TILE_SIZE)-TILE_SIZE)
		self.main.screen.blit(self.rendered_surface, offset)
		self.prev_offset = tuple(self.offset)
		self.prev_coords = tuple(self.coords)







