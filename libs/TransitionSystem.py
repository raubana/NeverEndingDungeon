from TileSystem import PitTile, Tile, Grid, TILE_SIZE, get_flattened_grid, WallTile
from common import invlerp, bezier

import math, random

def pick_random_transition():
	L = [LeftToRightWipe,RightToLeftWipe,TopToBottomWipe,BottomToTopWipe]
	return random.choice(L)

class Transition(object):
	def __init__(self, main, old_grid, new_grid, visible_grid, trans_len=120):
		self.main = main
		self.old_grid = old_grid
		self.new_grid = new_grid

		self.visible_grid = visible_grid
		self.done_transitioning = False
		self.transition = 0
		self.transition_length = trans_len

		self.update_frequency = 0
		self.last_update = int(self.update_frequency)

		#We create the transition grids.
		self.size = (max(old_grid.gridsize[0],new_grid.gridsize[0]),
					max(old_grid.gridsize[1],new_grid.gridsize[1]))

		self.trans_old_grid = Grid(self.main) #This is the resized version of the old_grid.
		self.trans_new_grid = Grid(self.main) #This is the resized version of the new_grid.
		self.trans_grid = Grid(self.main) #This is the grid that we see.

		self.preferred_offsets = []

		self.preferred_offsets.append( (-((self.old_grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)),
										-((self.old_grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2))) )
		self.preferred_offsets.append( (-((self.size[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)),
										-((self.size[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2))) )
		self.preferred_offsets.append( (-((self.new_grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)),
										-((self.new_grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2))) )

		self.trans_old_grid.gridsize = self.size
		self.trans_new_grid.gridsize = self.size
		self.trans_grid.gridsize = self.size

		self.trans_old_grid.tiles = []
		self.trans_new_grid.tiles = []
		self.trans_grid.tiles = []

		self.changed_tiles = []

		for y in xrange(self.size[1]):
			#We create the trans_old_grid rows.
			if y >= self.old_grid.gridsize[1]:
				trans_old_row = []
				for x in xrange(self.size[0]):
					trans_old_row.append(WallTile(main))
			else:
				#add new pits to the right of the old grid
				trans_old_row = list(old_grid.tiles[y])
				for x in xrange(self.size[0]-self.old_grid.gridsize[0]):
					trans_old_row.append(WallTile(main))
			self.trans_old_grid.tiles.append(trans_old_row)

			#We create the trans_new_grid rows.
			if y >= self.new_grid.gridsize[1]:
				trans_new_row = []
				for x in xrange(self.size[0]):
					trans_new_row.append(WallTile(main))
			else:
				#add new pits to the right of the old grid
				trans_new_row = list(new_grid.tiles[y])
				for x in xrange(self.size[0]-self.new_grid.gridsize[0]):
					trans_new_row.append(WallTile(main))
			self.trans_new_grid.tiles.append(trans_new_row)

			#We create the trans_grid rows (which starts off identical to the trans_old_grid)
			if y >= self.old_grid.gridsize[1]:
				trans_row = []
				for x in xrange(self.size[0]):
					trans_row.append(WallTile(main))
			else:
				#add new pits to the right of the old grid
				trans_row = list(old_grid.tiles[y])
				for x in xrange(self.size[0]-self.old_grid.gridsize[0]):
					trans_row.append(WallTile(main))
			self.trans_grid.tiles.append(trans_row)

		main.world.grid = self.trans_grid
		visible_grid.flag_for_rerender()

		self.init()

	def init(self):
		pass

	def update(self):
		self.changed_tiles = []
		rerender = False
		if not self.done_transitioning:
			self.transition += 1
			if self.transition > self.transition_length+1:
				self.done_transitioning = True
				self.main.world.grid = self.new_grid
				rerender = True
			else:
				p = self.transition/float(self.transition_length)
				self.last_update += 1
				if self.last_update >= self.update_frequency:
					self.last_update = 0
					for y in xrange(self.size[1]):
						for x in xrange(self.size[0]):
							inside_old = x < self.old_grid.gridsize[0] and y < self.old_grid.gridsize[1]
							inside_new = x < self.new_grid.gridsize[0] and y < self.new_grid.gridsize[1]
							if inside_old or inside_new:
								tile = self.get_transition_tile((x,y), p)
								if tile != self.trans_grid.tiles[y][x]:
									self.changed_tiles.append(((x,y), self.trans_grid.tiles[y][x], tile))
									self.trans_grid.tiles[y][x] = tile
									tile.flag_for_rerender()
									rerender = True
				p = invlerp(1,-1,math.cos(p*math.pi))
				self.main.world.preferred_offset = bezier(self.preferred_offsets, p)
		if rerender:
			self.visible_grid.flag_for_rerender()

	def get_transition_tile(self, tile_pos, trans_percent):
		"""
		This would be overridden by other transition types.
		This grabs a tile from either the trans_old_grid or the trans_new_grid and returns it.
		Which tile it grabs and from where depends on the tile_pos and the trans_percent.
		"""
		pass


class HintedTransition(object):
	def __init__(self, main, old_grid, new_grid, visible_grid, flat_len = 60, hint_delay = 60,
				 hint_len = 60, trans_delay = 120, trans_len = 60, flat_type = None,
				 hint_type = None, trans_type = None):
		#NOTE: NEVER MAKE THE LENGTH OF A TRANSITION LESS THAN 1!!

		self.main = main
		self.visible_grid = visible_grid

		self.flat_length = flat_len
		self.hint_delay = hint_delay
		self.hint_length = hint_len
		self.trans_delay = trans_delay
		self.trans_length = trans_len

		self.flat_type = flat_type
		self.hint_type = hint_type
		self.trans_type = trans_type

		if not self.flat_type: self.flat_type = pick_random_transition()
		if not self.hint_type: self.hint_type = pick_random_transition()
		if not self.trans_type: self.trans_type = pick_random_transition()

		self.stage = 1
		self.delay = 0

		new_size = (max(old_grid.gridsize[0],new_grid.gridsize[0]),
					max(old_grid.gridsize[1],new_grid.gridsize[1]))

		self.old_grid = old_grid
		self.flat_grid = Grid(main, new_size)
		self.hint_grid = get_flattened_grid(new_grid, new_size)
		self.new_grid = new_grid

		self.current_transition = self.flat_type(self.main,
												 self.old_grid,
												 self.flat_grid,
												 self.visible_grid,
												 self.flat_length)

		self.changed_tiles = []

		self.done_transitioning = False

	def update(self):
		self.changed_tiles = []
		if self.stage != 6:
			delay_amount = None
			if self.stage == 2: delay_amount = self.hint_delay
			elif self.stage == 4: delay_amount = self.trans_delay
			else:
				self.current_transition.update()
				self.changed_tiles = self.current_transition.changed_tiles
				if self.current_transition.done_transitioning:
					self.current_transition = None
					self.stage += 1
			if delay_amount != None:
				self.delay += 1
				if self.delay >= delay_amount:
					self.delay = 0
					self.stage += 1
					if self.stage == 3:
						self.current_transition = self.hint_type(self.main,
																 self.flat_grid,
																 self.hint_grid,
																 self.visible_grid,
																 self.hint_length)
					elif self.stage == 5:
						self.current_transition = self.hint_type(self.main,
																 self.hint_grid,
																 self.new_grid,
																 self.visible_grid,
																 self.trans_length)
		else:
			self.done_transitioning = True


class LeftToRightWipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		x_pos = self.size[0]*trans_percent
		if x_pos >= tile_pos[0]:
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class RightToLeftWipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		x_pos = self.size[0]*(1-trans_percent)
		if x_pos < tile_pos[0]:
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class VerticalInToOutWipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		x_pos1 = self.size[0]*trans_percent*0.5
		x_pos2 = self.size[0]*(1-(trans_percent*0.5))
		if x_pos1 >= tile_pos[0] or x_pos2 < tile_pos[0]:
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class BottomToTopWipe(Transition):
	#'Top' as it top of the screen.
	def get_transition_tile(self, tile_pos, trans_percent):
		y_pos = self.size[1]*(1-trans_percent)
		if y_pos < tile_pos[1]:
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class TopToBottomWipe(Transition):
	#'Top' as it top of the screen.
	def get_transition_tile(self, tile_pos, trans_percent):
		y_pos = self.size[1]*trans_percent
		if y_pos >= tile_pos[1]:
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class TLtoBRwipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = (self.size[0]+self.size[1])*trans_percent
		if total >= tile_pos[0]+tile_pos[1]:
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class SquareTLtoBRwipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = max(self.size)*trans_percent
		if total >= max(tile_pos):
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class SquareTRtoBLwipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = max(self.size)*trans_percent
		if total >= max((self.size[0]-tile_pos[0]-1,tile_pos[1])):
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class SquareBLtoTRwipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = max(self.size)*trans_percent
		if total >= max((tile_pos[0],self.size[1]-tile_pos[1]-1)):
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class SquareBRtoTLwipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = max(self.size)*trans_percent
		if total >= max((self.size[0]-tile_pos[0]-1,self.size[1]-tile_pos[1]-1)):
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class ReverseSquareTLtoBRwipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = max(self.size)*trans_percent
		if total >= min(tile_pos):
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class SquareTLtoBRreverseWipe(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = max(self.size)*(1-trans_percent)
		if total < max(tile_pos):
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]

class SquareOutToIn(Transition):
	def get_transition_tile(self, tile_pos, trans_percent):
		total = max(self.size)*trans_percent*0.5
		if total >= tile_pos[0] or total >= tile_pos[1] or total >= self.size[0]-tile_pos[0]-1 or total >= self.size[1]-tile_pos[1]-1:
			return self.trans_new_grid.tiles[tile_pos[1]][tile_pos[0]]
		else:
			return self.trans_old_grid.tiles[tile_pos[1]][tile_pos[0]]