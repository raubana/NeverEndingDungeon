import pygame
from pygame.locals import*

from TileSystem import Grid, VisibleGrid, Tile, WallTile, PitTile, TILE_SIZE, round_coords, offset_to_coords
from Entities.Player import Player
from Entities.Baddie1 import Baddie1
from common import lerp_pos, lerp_colors, lerp
from TransitionSystem import *

import random


DEBUG_DISABLE_FOLLOW_PLAYER = False

class World(object):
	"""
	This is the World! It contains all entities, sprites, particles, tiles, and many other things.
	"""
	def __init__(self, main):
		self.main = main

		self.grid = Grid(main, (11,9))
		for y in xrange(self.grid.gridsize[1]):
			for x in xrange(self.grid.gridsize[0]):
				if not (x == 5 and y == 4):
					self.grid.tiles[y][x] = PitTile(self.main)

		self.transition = None

		self.visible_grid = VisibleGrid(main)

		self.player = Player(main, [(self.grid.gridsize[0]*TILE_SIZE)/2, (self.grid.gridsize[1]*TILE_SIZE)/2], [28,28])
		self.player_is_alive = True

		self.npcs = []
		self.particles = []

		self.preferred_offset = (-((self.grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)), -((self.grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2)))

		#new_offset = ((0) - (self.main.screen_size[0]/2), (0) - (self.main.screen_size[1]/2))
		self.visible_grid.set_offset(self.preferred_offset)

		self.sounds = {}

		self.sounds["enemy_death"] = pygame.mixer.Sound("snds/sfx/enemy_death.wav")
		self.sounds["enemy_hurt"] = pygame.mixer.Sound("snds/sfx/enemy_hurt.wav")
		self.sounds["falling"] = pygame.mixer.Sound("snds/sfx/falling.wav")
		self.sounds["player_hurt"] = pygame.mixer.Sound("snds/sfx/player_hurt.wav")
		self.sounds["player_death"] = pygame.mixer.Sound("snds/sfx/player_death.wav")
		self.sounds["sword_swing"] = pygame.mixer.Sound("snds/sfx/sword_swing.wav")

		self.load_main_script()

	def load_main_script(self):
		self.main_script = self.load_script("main_script")
		self.main_script_index = 0

	def load_script(self, filename):
		f = open("data/scripts/"+filename+".txt")
		s = f.read().split("\n")
		f.close()
		new_s = []
		while len(s) > 0:
			line = s.pop(0).strip()
			if line.startswith("script "): # This allows for compounding of separate scripts.
				s = self.load_script(line[len("script "):]) + s
			else:
				new_s.append(line)
		return new_s

	def play_sound(self, soundname, offset):
		#first we check if the sound exists
		if soundname in self.sounds:
			sound = self.sounds[soundname]
			x_pos = self.visible_grid.offset[0]+offset[0]
			x_pos = min(max(x_pos,0), self.main.screen_size[0])
			p = x_pos/float(self.main.screen_size[0])
			L_vol = max(min((1-p)*2,1.0),0.0)
			R_vol = max(min(p*2,1.0),0.0)

			channel = sound.play()
			if channel:
				channel.set_volume(L_vol, R_vol)
		else:
			print "That sound doesn't exist: ", soundname

	def prep_next_grid(self):
		#We set the current grid to be a flat area.
		new_size = (11,9)
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
		return next_grid

	def parse_script(self):
		stop = False
		while not stop:
			if self.main_script_index < len(self.main_script):
				line = self.main_script[self.main_script_index]
				print line
				if line.startswith("load_song "):
					song = line[len("load_song "):]
					self.main.music.load_music(song)
				elif line == "play_music":
					self.main.music.begin()
				elif line.startswith("cue_music "):
					cued = line[len("cue_music "):]
					self.main.music.cue(int(cued))
				elif line.startswith("hard_cue_music "):
					cued = line[len("hard_cue_music "):]
					self.main.music.cue(int(cued), True)
				elif line.startswith("wait "):
					wait = line[len("wait "):]
					if wait.startswith("current_music "):
						music = int(wait[len("current_music "):])
						if self.main.music.current != music:
							stop = True
					elif wait.startswith("music_pos "):
						pos = float(wait[len("music_pos "):])
						if not (self.main.music.prev_sound_pos < pos and (self.main.music.sound_pos >= pos or self.main.music.sound_pos < self.main.music.prev_sound_pos)):
							stop = True
				if not stop:
					self.main_script_index += 1
			else:
				stop = True

	def update(self):
		"""
		World.update - Called by Main.
		Updates all entities and handles/performs events.
		Dead entities are pruned in this function.
		"""

		#Updates the script
		self.parse_script()

		if not self.player.dead:
			if self.transition != None:
				self.transition.update()
				#if self.transition.done_transitioning:
				#	self.transition = None
				if not self.transition.done_transitioning:
					if self.transition.stage == 2 and self.transition.delay == 0:
						for x in xrange(5):
							pos = ((random.randint(0,self.grid.gridsize[0])*0.5)*TILE_SIZE,
								   (random.randint(0,self.grid.gridsize[1])*0.5)*TILE_SIZE)
							self.npcs.append(Baddie1(self.main, pos))
						self.player.is_hurt = True
						self.player.hurt = self.player.hurt_length

					if self.transition.stage >= 2 or self.transition.stage == 0:
						if len(self.npcs) == 0:
							if self.main.music.current == 2:
								self.main.music.cue(3)
						else:
							if self.main.music.current == 3:
								self.main.music.cue(2)
				else:
					next_grid = self.prep_next_grid()
					self.transition = HintedTransition(self.main, self.grid, next_grid, self.visible_grid, flat_delay=400)
			else:
				if self.main.music.current == 1 and self.main.music.sound_pos >= self.main.music.intro_trans_beats-1:
					next_grid = self.prep_next_grid()
					self.transition = HintedTransition(self.main, self.grid, next_grid, self.visible_grid, flat_delay=0, flat_len=1)

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
		else:
			if self.player_is_alive:
				self.player_is_alive = False
				self.visible_grid.apply_filter((255,0,0), BLEND_RGB_MIN)
				self.main.music.stop()
				self.main.world.play_sound("player_death", self.player.pos)
		"""
		for e in self.main.events:
			if e.type == MOUSEBUTTONDOWN and e.button == 1:
				pos = (self.visible_grid.offset[0]-e.pos[0]+(TILE_SIZE),
						self.visible_grid.offset[1]-e.pos[1]+(TILE_SIZE))
				pos = offset_to_coords(pos)
				pos = round_coords(pos)
				pos = ((pos[0]+0.5)*TILE_SIZE, (pos[1]+0.5)*TILE_SIZE)
				self.npcs.append(Baddie1(self.main, pos))
		"""

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
		if not DEBUG_DISABLE_FOLLOW_PLAYER:
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
			#Draws it's path
			if len(npc.path) > 2:
				new_path = []
				for pos in npc.path:
					new_path.append((pos[0]+offset[0], pos[1]+offset[1]))

				pygame.draw.lines(self.main.screen, (255,255,0), False, new_path, 2)

			#Draws it's current target position
			if npc.target_pos != None:
				pos = (npc.target_pos[0]+offset[0], npc.target_pos[1]+offset[1])
				pygame.draw.circle(self.main.screen, (255,255,0), pos, 4)

			#Draws it's coordinates
			if npc.target_pos != None:
				pos = (int((npc.coords[0]+0.5)*TILE_SIZE+offset[0]), int((npc.coords[1]+0.5)*TILE_SIZE+offset[1]))
				pygame.draw.circle(self.main.screen, (255,255,255), pos, 4)

		#Draws players's coordinates
		pos = (int(self.player.pos[0]+offset[0]), int(self.player.pos[1]+offset[1]))
		pygame.draw.circle(self.main.screen, (255,255,255), pos, 4)
		"""
