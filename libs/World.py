import pygame
from pygame.locals import*

from TileSystem import Grid, VisibleGrid, Tile, WallTile, PitTile, TILE_SIZE
from Entities.Player import Player
from Entities.Baddie1 import Baddie1
from common import lerp_pos, lerp_colors
from TransitionSystem import *

import random

class World(object):
	"""
	This is the World! It contains all entities, sprites, particles, tiles, and many other things.
	"""
	def __init__(self, main):
		self.main = main

		self.grid = Grid(main)

		#For testing purposes.
		self.grid.gridsize = (5,5)
		self.grid.tiles = []
		for y in xrange(self.grid.gridsize[1]):
			row = []
			for x in xrange(self.grid.gridsize[0]):
				tile = Tile(main)
				row.append(tile)
			self.grid.tiles.append(row)

		self.transition = None

		self.visible_grid = VisibleGrid(main)

		self.player = Player(main, [(self.grid.gridsize[0]*TILE_SIZE)/2, (self.grid.gridsize[1]*TILE_SIZE)/2], [24,24])

		self.npcs = []
		self.particles = []
		"""
		self.npcs.append(Baddie1(main, (TILE_SIZE/2,TILE_SIZE/2)))
		self.npcs.append(Baddie1(main, (((self.grid.gridsize[0]-1)*TILE_SIZE)+TILE_SIZE/2,((self.grid.gridsize[1]-1)*TILE_SIZE)+TILE_SIZE/2)))
		"""
		self.preferred_offset = (-((self.grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)), -((self.grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2)))

		#new_offset = ((0) - (self.main.screen_size[0]/2), (0) - (self.main.screen_size[1]/2))
		self.visible_grid.set_offset(self.preferred_offset)

	def prep_next_grid(self):
		#We set the current grid to be a flat area.
		new_size = (random.randint(6,10), random.randint(6,10))
		#We setup the next grid.
		next_grid = Grid(self.main)
		next_grid.gridsize = new_size
		next_grid.tiles = []
		for y in xrange(new_size[1]):
			row = []
			for x in xrange(new_size[0]):
				if random.randint(0,3) == 0:
					tile = WallTile(self.main)
				elif random.randint(0,4) == 0:
					tile = PitTile(self.main)
				else:
					tile = Tile(self.main)
				row.append(tile)
			next_grid.tiles.append(row)
		self.transition = HintedTransition(self.main, self.grid, next_grid, self.visible_grid)

	def update(self):
		"""
		World.update - Called by Main.
		Updates all entities and handles/performs events.
		Dead entities are pruned in this function.
		"""
		if self.transition != None and not self.player.dead:
			self.transition.update()
			if self.transition.done_transitioning:
				self.transition = None

		#Updates the player.
		self.player.update()

		if not self.player.dead:
			#Then updates/prunes NPCs.
			i = len(self.npcs) - 1
			while i >= 0:
				self.npcs[i].update()
				npc = self.npcs[i]
				if npc.dead and not (npc.is_dying or npc.falling):
					del self.npcs[i]
				i -= 1

			#Then updates/prunes particles.
			i = len(self.particles) - 1
			while i >= 0:
				self.particles[i].update()
				if self.particles[i].dead:
					del self.particles[i]
				i -= 1

		for e in self.main.events:
			if e.type == KEYDOWN and e.key == K_p:
				self.transition = 0
				self.transitioning = True
				self.prep_next_grid()

	def move(self):
		"""
		World.move - Called by Main.
		Calls 'move' on all entities.
		"""
		self.player.move()
		if not self.player.dead:
			for npc in self.npcs:
				npc.move()
			for particle in self.particles:
				particle.move()

		# === MOVES THE 'CAMERA' ===

		#first we center it.
		new_offset = list(self.preferred_offset)
		#then we check if the player is almost going off of the screen.
		pl = self.player
		offset = [0,0]
		inset = 200
		rect = pygame.Rect([-new_offset[0]+inset,
							-new_offset[1]+inset,
							self.main.screen_size[0]-inset-inset,
							self.main.screen_size[1]-inset-inset])
		left = pl.rect.left - rect.right
		top = pl.rect.top - rect.bottom
		right = rect.left - pl.rect.right
		bottom = rect.top - pl.rect.bottom
		m = max(left,top,right,bottom)
		if m > 0:
			if abs(offset[0]) < left: offset[0] = left
			if abs(offset[1]) < top: offset[1] = top
			if abs(offset[0]) < right: offset[0] = -right
			if abs(offset[1]) < bottom: offset[1] = -bottom

			new_offset = (new_offset[0]-offset[0],
							new_offset[1]-offset[1])
		#finally, we apply the new offset.
		self.visible_grid.set_offset(lerp_pos(self.visible_grid.offset, new_offset, 0.1))

	def render(self):
		"""
		World.render - Called by Main.
		Renders the world and it's contents to the screen.
		"""
		#first we render the background.
		self.visible_grid.render()
		for npc in self.npcs:
			npc.render()
		for particle in self.particles:
			particle.render()
		self.player.render()

		offset = self.visible_grid.offset
		"""
		for npc in self.npcs:
			if len(npc.path) > 2:
				new_path = []
				for pos in npc.path:
					new_path.append((pos[0]+offset[0], pos[1]+offset[1]))

				pygame.draw.lines(self.main.screen, (255,255,0), False, new_path, 2)
		"""