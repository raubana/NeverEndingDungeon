import pygame

from TileSystem import Grid, VisibleGrid, Tile, TILE_SIZE
from Entities.Player import Player

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
				row.append(Tile(main))
			self.grid.tiles.append(tuple(row))

		self.visible_grid = VisibleGrid(main)

		self.players = []
		#For testing purposes
		self.players.append(Player(main, [(self.grid.gridsize[0]*TILE_SIZE)/2, (self.grid.gridsize[1]*TILE_SIZE)/2]))

		self.npcs = []
		self.particles = []

	def update(self):
		"""
		World.update - Called by Main.
		Updates all entities and handles/performs events.
		Dead entities are pruned in this function.
		"""
		#First updates/prunes players.
		i = len(self.players) - 1
		while i >= 0:
			self.players[i].update()
			if self.players[i].dead:
				del self.players[i]
			i -= 1

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
		for player in self.players:
			player.move()
		for npc in self.npcs:
			npc.move()
		for particle in self.particles:
			particle.move()

		#moves the 'camera'
		if len(self.players) > 0:
			pl = self.players[0]
			new_offset = (-((self.grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)), -((self.grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2)))
			#new_offset = (-(pl.pos[0] - (self.main.screen_size[0]/2)), -(pl.pos[1] - (self.main.screen_size[1]/2)))
			self.visible_grid.set_offset(new_offset)

	def render(self):
		"""
		World.render - Called by Main.
		Renders the world and it's contents to the screen.
		"""
		#first we render the background.
		self.visible_grid.render()
		for player in self.players:
			player.render()
		for npc in self.npcs:
			npc.render()
		for particle in self.particles:
			particle.render()