# ====== IMPORTS ======
# --- Pygame ---
import pygame

# --- Custom Modules ---
from common import copy_color, lerp_colors

# --- Misc. ---
import random, math

# ====== CONSTANTS ======
TILE_SIZE = 48  # The 2D size of a side of a single tile in pixels.

TILE_FLOOR_COLOR = (96,96,96)
TILE_FLATTENED_COLOR = (127,127,127)
TILE_WALLTILE_COLOR = (96,127,160)
TILE_PIT_COLOR = (0,0,0)

TILE_HINT_COLOR_STRENGTH = 0.5

OUTLINE_NORMAL = 1
OUTLINE_OUTSET = 2
OUTLINE_INSET = 3


DEBUG_FORCE_FULL_RERENDER = False


# ====== FUNCTIONS ======
def offset_to_coords(offset):
	"""This is for converting a VisibleGrid's offset to coordinates,
	which tell us which tile is in the top-left corner."""
	return (-int(offset[0]/TILE_SIZE), -int(offset[1]/TILE_SIZE))

def round_coords(coords):
	return (int(math.floor(coords[0])), int(math.floor(coords[1])))

def get_flattened_grid(grid, size = None):
	if size == None:
		size = grid.gridsize
	new_grid = Grid(grid.main)
	new_grid.gridsize = size
	new_grid.tiles = []
	for y in xrange(size[1]):
		row = []
		for x in xrange(size[0]):
			is_pit = False
			is_solid = False
			new_tile = Tile(grid.main)
			new_tile.color = TILE_FLATTENED_COLOR
			if x < grid.gridsize[0] and y < grid.gridsize[1]:
				color = grid.tiles[y][x].color
				if grid.tiles[y][x].is_a_pit:
					is_pit = True
				elif grid.tiles[y][x].solid:
					is_solid = True
			else:
				color = TILE_PIT_COLOR
				is_pit = True
			new_tile.color = lerp_colors(new_tile.color, color, TILE_HINT_COLOR_STRENGTH)
			if is_pit:
				new_tile.outline_type = OUTLINE_NORMAL
				new_tile.outline_strength = 0.025
			else:
				new_tile.outline_type = OUTLINE_OUTSET
			row.append(new_tile)
		new_grid.tiles.append(row)
	return new_grid



# ====== CLASSES ======
class Grid(object):
	"""
	This class contains the tiles of the entire world.
	"""
	def __init__(self, main, size = (0,0)):
		self.main = main

		self.gridsize = size # in tiles.
		self.tiles = []
		for y in xrange(size[1]):
			row = []
			for x in xrange(size[0]):
				row.append(Tile(main))
			self.tiles.append(row)

	def is_legal_coords(self, coords, ignore_type = False):
		"""
		Checks if the given coordinates are within the world
		(specifically meaning if a tile exists at that exact location).
		"""
		#first we check if this coord is within the bounds of the grid.
		if coords[0] < 0 or coords[1] < 0 or coords[0] >= self.gridsize[0] or coords[1] >= self.gridsize[1]:
			return False
		#next we check if there's a tile at this location.
		if ignore_type:
			return True
		pos = round_coords(coords)
		return not self.tiles[pos[1]][pos[0]].is_a_pit

	def get_path(self, start_coords, end_coords, avoid_mob=True, shit_path_freq=0.1):
		#We also assume that the mobs can not go diagonally.
		#Shit paths are when the algorithm take into account stupid and often longer paths.
		start = (int(start_coords[0]),int(start_coords[1]))
		end = (int(end_coords[0]),int(end_coords[1]))

		open_list = []
		closed_list = []

		#we start by adding the start_coords to the open_list
		# (pos, prev pos, total distance covered, score)
		open_list.append( (start, [start], 0, self.score_coords(start, start, end, 0, avoid_mob)) )

		#now we start our loop
		while len(open_list) > 0:
			#we need to find our best scores in the open list
			best_score = None
			best_scores = []
			for tile in open_list:
				if best_score == None or tile[3] < best_score:
					best_score = tile[3]
					best_scores = [tile]
				elif tile[3] <= best_score+1 and random.random() < shit_path_freq: #This is to add a little randomness, so that mob don't overlap too often.
					best_scores.append(tile)
			#now we pick from those
			pick = random.choice(best_scores)
			#we need to move this tile from the open list to the closed list
			open_list.remove(pick)
			closed_list.append(pick)
			#we need to check if that was the end_coords, in which case we'll drop from the loop.

			#we need to put all of the neighbors into the open list
			offsets = ((-1,0),(0,-1),(1,0),(0,1))
			for offset in offsets:
				pos = (pick[0][0]+offset[0], pick[0][1]+offset[1])
				#we need to check if this is a legal position
				if self.is_legal_coords(pos):
					#next we check if it's an open and safe tile
					tile = self.tiles[pos[1]][pos[0]]
					if tile != None and not tile.solid:
						#next we must check if this pos is already in the open or closed lists
						match = False
						for pos2 in open_list+closed_list:
							if pos2[0] == pos:
								match = True
								break
						if not match:
							#This is a legal pos and it's not already in any of the lists, so we add it to the open_list.
							dist_covered = pick[2]+abs(pick[0][0]-pos[0])+abs(pick[0][1]-pos[1])
							open_list.append( (pos, pick, dist_covered, self.score_coords(pos, pick[1][0], end, dist_covered, avoid_mob)) )

		#first we must find our closest tile in the closed_list
		closest_dist = None
		closest_tile = None
		for tile in closed_list:
			dif = abs(tile[0][0]-end[0]) + abs(tile[0][1]-end[1])
			if closest_dist == None or dif < closest_dist:
				closest_dist = dif
				closest_tile = tile
		#now we work our way backwards to get our path
		current_tile = closest_tile
		path = []
		while current_tile[1][0] != current_tile[0]:
			pos = current_tile[0]
			pos = (pos[0]*TILE_SIZE+(TILE_SIZE/2),
					pos[1]*TILE_SIZE+(TILE_SIZE/2))
			path.append(pos)
			current_tile = current_tile[1]
		pos = (start[0]*TILE_SIZE+(TILE_SIZE/2),
					start[1]*TILE_SIZE+(TILE_SIZE/2))
		path.append(pos)
		path.reverse()
		#finally we return our path
		return path

	def score_coords(self, prev_coords, end_coords, target_coords, prev_distance, avoid_mob):
		prev = (int(prev_coords[0]),int(prev_coords[1]))
		end = (int(end_coords[0]),int(end_coords[1]))
		target = (int(target_coords[0]),int(target_coords[1]))

		new_score = int(prev_distance)

		dif = (end[0]-target[0], end[1]-target[1])
		dist = (dif[0]**2 + dif[1]**2)**0.5

		new_score += dist

		new_score += abs(end[0]-prev[0])
		new_score += abs(end[1]-prev[1])

		if avoid_mob:
			occupied = False
			#rect = pygame.Rect([end_coords[0]*TILE_SIZE,end_coords[1]*TILE_SIZE,TILE_SIZE,TILE_SIZE])
			for npc in self.main.world.npcs:
				"""
				if npc.rect.colliderect(rect):
					left = rect.right - npc.rect.left
					top = rect.bottom - npc.rect.top
					right = npc.rect.right - rect.left
					bottom = npc.rect.bottom - rect.top

					m = min(left,top,right,bottom)
					if m > 0:
				"""
				if end_coords == npc.coords:
					occupied = True
					break
			if occupied:
				new_score += 10

		return new_score



class Tile(object):
	def __init__(self, main):
		self.main = main
		self.solid = False
		self.is_a_pit = False
		self.flag_for_rerender()
		self.rendered_surface = pygame.Surface((TILE_SIZE,TILE_SIZE))
		self.color = copy_color(TILE_FLOOR_COLOR)
		self.outline_strength = 0.1
		self.outline_size = 1
		self.outline_type = OUTLINE_OUTSET
		self.init()

	def init(self):
		pass

	def set_color(self, new_color):
		if new_color != self.color:
			self.color = new_color
			self.flag_for_rerender()

	def flag_for_rerender(self):
		self.flagged_for_rerender = True

	def rerender(self):
		if self.flagged_for_rerender:
			self.flagged_for_rerender = False
			color = self.color
			if self.outline_size > 0:
				if self.outline_type == OUTLINE_NORMAL:
					self.rendered_surface.fill(color)
					outline_color = lerp_colors(color, (0,0,0), self.outline_strength)
					pygame.draw.rect(self.rendered_surface, outline_color, (0,0,TILE_SIZE,TILE_SIZE), self.outline_size)
				elif self.outline_type in (OUTLINE_INSET, OUTLINE_OUTSET):
					self.rendered_surface.fill(lerp_colors(color, (0,0,0), self.outline_strength*0.5))
					c1 = lerp_colors(color, (255,255,255), self.outline_strength*0.25)
					c2 = lerp_colors(color, (0,0,0), self.outline_strength)
					if self.outline_type == OUTLINE_INSET:
						c1,c2 = c2,c1
					p1 = (self.outline_size, TILE_SIZE-self.outline_size)
					p2 = (TILE_SIZE-self.outline_size, self.outline_size)
					p3 = (self.outline_size,self.outline_size)
					p4 = (TILE_SIZE-self.outline_size,TILE_SIZE-self.outline_size)
					pygame.draw.polygon(self.rendered_surface, c1, ((0,0),(TILE_SIZE,0),p2,p3,p1,(0,TILE_SIZE)))
					pygame.draw.polygon(self.rendered_surface, c2, ((TILE_SIZE,TILE_SIZE),(0,TILE_SIZE),p1,p4,p2,(TILE_SIZE,0)))

	def render(self, surface, pos):
		self.rerender()
		surface.blit(self.rendered_surface, pos)

class WallTile(Tile):
	def init(self):
		self.solid = True
		self.color = copy_color(TILE_WALLTILE_COLOR)
		self.outline_strength = 0.35
		self.outline_size = 3
		self.outline_type = OUTLINE_OUTSET

class PitTile(Tile):
	def init(self):
		self.is_a_pit = True
		self.color = copy_color(TILE_PIT_COLOR)
		self.outline_type = OUTLINE_INSET
		self.outline_size = 0



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

		self.filter = 0
		self.filter_color = (255,255,255)

		wall = WallTile(self.main)
		wall.rerender()

		self.wall_texture = wall.rendered_surface

		for y in xrange(self.gridsize[1]):
			for x in xrange(self.gridsize[0]):
				self.rendered_surface.blit(self.wall_texture, (x*TILE_SIZE,y*TILE_SIZE))

	def apply_filter(self, filter_color, filter_type):
		self.filter = filter_type
		self.filter_color = filter_color
		self.rendered_surface.fill(filter_color, None, filter_type)

	def calc_gridsize(self):
		return (self.main.screen_size[0] / TILE_SIZE + 2, self.main.screen_size[1] / TILE_SIZE + 2)

	def set_offset(self, offset):
		offset = (int(offset[0]),int(offset[1]))
		if offset != self.offset:
			self.offset = offset
			new_coords = offset_to_coords(offset)
			if new_coords != self.coords:
				#if new_coords == self.prev_coords:
				#	self.unflag_for_rerender()
				#else:
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
		if self.flagged_for_rerender or DEBUG_FORCE_FULL_RERENDER:
			self.flagged_for_rerender = False

			coord_dif = (self.coords[0]-self.prev_coords[0], self.coords[1]-self.prev_coords[1])

			#first we try to reuse some of the old stuff again.
			if (coord_dif[0] != 0 or coord_dif[1] != 0) and abs(coord_dif[0]) < self.gridsize[0] and abs(coord_dif[1]) < self.gridsize[1]:
				if not DEBUG_FORCE_FULL_RERENDER:
					self.rendered_surface.blit(self.rendered_surface,(-coord_dif[0]*TILE_SIZE, -coord_dif[1]*TILE_SIZE))

			# next we check for any tiles that need to be rendered to the surface,
			# including those that may have simply changed their appearance.
			for x in xrange(self.gridsize[0]):
				for y in xrange(self.gridsize[1]):
					is_new_tile = bool(DEBUG_FORCE_FULL_RERENDER)
					is_new_tile = is_new_tile or (coord_dif[0] < 0 and x < -coord_dif[0])
					is_new_tile = is_new_tile or (coord_dif[1] < 0 and y < -coord_dif[1])
					is_new_tile = is_new_tile or (coord_dif[0] > 0 and x >= self.gridsize[0]-coord_dif[0])
					is_new_tile = is_new_tile or (coord_dif[1] > 0 and y >= self.gridsize[1]-coord_dif[1])

					pos = (x+self.coords[0]-1,y+self.coords[1]-1)
					if self.main.world.grid.is_legal_coords(pos, ignore_type = True):
						tile = self.main.world.grid.tiles[pos[1]][pos[0]]
					else:
						tile = None

					if (tile != None and (tile.flagged_for_rerender or is_new_tile)) or (tile == None and is_new_tile):
						if tile:
							# We tell the tile to render to the surface.
							tile.render(self.rendered_surface, (x*TILE_SIZE,y*TILE_SIZE))
						else:
							self.rendered_surface.blit(self.wall_texture,(x*TILE_SIZE,y*TILE_SIZE))
							#self.rendered_surface.fill((0,0,0),(x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))

					if self.filter != 0:
						self.rendered_surface.fill(self.filter_color, (x*TILE_SIZE,y*TILE_SIZE, TILE_SIZE, TILE_SIZE), special_flags=self.filter)

	def render(self):
		"""
		Render is only called by world or main.
		"""
		self.rerender() #In case the pre-rendered surface needs to be changed.
		offset = (int(self.offset[0]%TILE_SIZE)-TILE_SIZE, int(self.offset[1]%TILE_SIZE)-TILE_SIZE)
		self.main.screen.blit(self.rendered_surface, offset)
		self.prev_offset = tuple(self.offset)
		self.prev_coords = tuple(self.coords)







