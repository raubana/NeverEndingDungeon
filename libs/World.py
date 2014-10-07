import pygame
from pygame.locals import*

from TileSystem import Grid, VisibleGrid, Tile, WallTile, TILE_SIZE
from Entities.Player import Player
from Entities.Baddie1 import Baddie1

import random

class World(object):
	"""
	This is the World! It contains all entities, sprites, particles, tiles, and many other things.
	"""
	def __init__(self, main):
		self.main = main

		self.grid = Grid(main)

		#For testing purposes.
		self.grid.gridsize = (8,8)
		self.grid.tiles = []
		for y in xrange(self.grid.gridsize[1]):
			row = []
			for x in xrange(self.grid.gridsize[0]):
				if random.randint(0,3) == 0:
					tile = WallTile(main)
				else:
					tile = Tile(main)
				row.append(tile)
			self.grid.tiles.append(tuple(row))

		self.visible_grid = VisibleGrid(main)

		self.player = Player(main, [(self.grid.gridsize[0]*TILE_SIZE)/2, (self.grid.gridsize[1]*TILE_SIZE)/2])

		self.npcs = []
		self.particles = []

		self.npcs.append(Baddie1(main, (TILE_SIZE/2,TILE_SIZE/2)))

		new_offset = (-((self.grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)), -((self.grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2)))
		#new_offset = ((0) - (self.main.screen_size[0]/2), (0) - (self.main.screen_size[1]/2))
		self.visible_grid.set_offset(new_offset)

	def update(self):
		"""
		World.update - Called by Main.
		Updates all entities and handles/performs events.
		Dead entities are pruned in this function.
		"""
		#Updates the player.
		self.player.update()

		if not self.player.dead:
			#Then updates/prunes NPCs.
			i = len(self.npcs) - 1
			while i >= 0:
				self.npcs[i].update()
				if self.npcs[i].dead:
					del self.npcs[i]
				i -= 1

			#Then updates/prunes particles.
			i = len(self.particles) - 1
			while i >= 0:
				self.particles[i].update()
				if self.particles[i].dead:
					del self.particles[i]
				i -= 1

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

		#moves the 'camera'

		#first we center it.
		new_offset = (-((self.grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)), -((self.grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2)))
		#new_offset = ((0) - (self.main.screen_size[0]/2), (0) - (self.main.screen_size[1]/2))
		self.visible_grid.set_offset(new_offset)

		pl = self.player

		offset = [0,0]
		inset = 200
		rect = pygame.Rect([-self.visible_grid.offset[0]+inset,
							-self.visible_grid.offset[1]+inset,
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

			new_offset = (self.main.world.visible_grid.offset[0]-offset[0],
							self.main.world.visible_grid.offset[1]-offset[1])
			self.visible_grid.set_offset(new_offset)

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