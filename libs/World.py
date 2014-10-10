import string
import pygame
from pygame.locals import*

from TileSystem import *
from Entities.Player import Player
from Entities.Baddie1 import Baddie1
from common import lerp_pos, lerp_colors, lerp
from TransitionSystem import *
from Script import Script

import random, os
from libs.FadeSystem import FadeToBlack, FadeFromBlack


class World(object):
	"""
	This is the World! It contains all entities, sprites, particles, tiles, and many other things.
	"""
	def __init__(self, main):
		self.main = main

		self.current_frame = long(0)
		self.paused = False

		self.grid = Grid(main, (1,1))

		self.transition = None
		self.silent_transitions = False
		self.fade = FadeFromBlack(self.main)

		self.earthquake_amount = 0
		self.earthquake_sound = pygame.mixer.Sound("snds/sfx/earthquake.wav")
		self.earthquake_sound_channel = pygame.mixer.Channel(0)

		self.visible_grid = VisibleGrid(main)

		self.player = Player(main, [(self.grid.gridsize[0]*TILE_SIZE)/2, (self.grid.gridsize[1]*TILE_SIZE)/2], [28,28])
		self.player_is_alive = True

		self.npcs = []
		self.particles = []

		self.preferred_offset = (-((self.grid.gridsize[0]*TILE_SIZE*0.5) - (self.main.screen_size[0]/2)), -((self.grid.gridsize[1]*TILE_SIZE*0.5) - (self.main.screen_size[1]/2)))
		self.disable_update_offset = False

		#new_offset = ((0) - (self.main.screen_size[0]/2), (0) - (self.main.screen_size[1]/2))
		self.visible_grid.set_offset(self.preferred_offset)

		self.sounds = {}

		self.sounds["enemy_death"] = pygame.mixer.Sound("snds/sfx/enemy_death.wav")
		self.sounds["enemy_hurt"] = pygame.mixer.Sound("snds/sfx/enemy_hurt.wav")
		self.sounds["falling"] = pygame.mixer.Sound("snds/sfx/falling.wav")
		self.sounds["player_hurt"] = pygame.mixer.Sound("snds/sfx/player_hurt.wav")
		self.sounds["player_death"] = pygame.mixer.Sound("snds/sfx/player_death.wav")
		self.sounds["sword_swing"] = pygame.mixer.Sound("snds/sfx/sword_swing.wav")
		self.sounds["tile_change"] = pygame.mixer.Sound("snds/sfx/tile_change.wav")
		self.sounds["tile_change_color"] = pygame.mixer.Sound("snds/sfx/tile_change_color.wav")
		self.sounds["death_music"] = pygame.mixer.Sound("snds/songs/death_music.ogg")
		self.sounds["pause_sound"] = pygame.mixer.Sound("snds/misc/pause_sound.wav")

		self.sounds["room1"] = pygame.mixer.Sound("snds/vo/room1.ogg")
		self.sounds["room2"] = pygame.mixer.Sound("snds/vo/room2.ogg")
		self.sounds["roomlaugh1"] = pygame.mixer.Sound("snds/vo/roomlaugh1.ogg")

		self.scripts = []

		self.load_startup_script()

	def autosave(self):
		f = open("save.dat", 'w')
		data = [self.scripts[0].filename]
		if self.main.music.songname != None and self.main.music.current != None:
			data.append(self.main.music.songname)
			data.append(str(self.main.music.current))
		data = string.join(data,"\n")
		#print "AUTOSAVE: "
		#print data
		f.write(data)
		f.close()

	def check_for_save(self):
		return os.path.exists("save.dat")

	def load_startup_script(self):
		#This is the script that's loaded when the program is started.
		if self.check_for_save():
			self.scripts.insert(0, Script(self, "startscreen/continue_screen"))
		else:
			self.scripts.insert(0, Script(self, "startscreen/newgame_screen"))

	def start_new_game(self):
		self.scripts.insert(0, Script(self, "level1/main_script"))

	def continue_saved_game(self):
		f = open("save.dat")
		data = f.read().split("\n")
		f.close()
		self.scripts = [Script(data[0])]
		if len(data) > 1:
			self.main.music.load_song(data[1])
			self.main.music.cue(int(data[2]), True)

	def play_sound(self, soundname, offset = None, volume = 1.0):
		#first we check if the sound exists
		if soundname in self.sounds:
			sound = self.sounds[soundname]
			if offset:
				x_pos = self.visible_grid.offset[0]+offset[0]
				x_pos = min(max(x_pos,0), self.main.screen_size[0])
				p = x_pos/float(self.main.screen_size[0])
				L_vol = max(min((1-p)*2,1.0),0.0)
				R_vol = max(min(p*2,1.0),0.0)
			else:
				L_vol = 1.0
				R_vol = 1.0

			L_vol *= volume
			R_vol *= volume

			channel = sound.play()
			if channel:
				channel.set_volume(L_vol, R_vol)
		else:
			print "That sound doesn't exist: ", soundname

	def load_grid(self, filename):
		f = open("data/grids/"+filename+".txt")
		data = f.read().split("\n")
		f.close()
		line = data.pop(0)
		parts = line.split(",")
		size = (int(parts[0]), int(parts[1]))

		grid = Grid(self.main)
		grid.gridsize = size
		grid.tiles = []

		for y in xrange(size[1]):
			row = []
			line = list(data.pop(0))
			for s in line:
				if s in "_-wpe":
					row.append(Tile(self.main))
					if s == "-":
						row[-1].color = lerp_colors(TILE_FLATTENED_COLOR, TILE_FLOOR_COLOR, TILE_HINT_COLOR_STRENGTH)
					elif s == "w":
						row[-1].color = lerp_colors(TILE_FLATTENED_COLOR, TILE_WALLTILE_COLOR, TILE_HINT_COLOR_STRENGTH)
					elif s == "p":
						row[-1].color = lerp_colors(TILE_FLATTENED_COLOR, TILE_PIT_COLOR, TILE_HINT_COLOR_STRENGTH)
					elif s == "e":
						row[-1].color = lerp_colors(TILE_FLATTENED_COLOR, TILE_SPAWNERTILE_COLOR, TILE_HINT_COLOR_STRENGTH)
				elif s in "123456789":
					row.append(TriggerTile(self.main))
					row[-1].id = s
				elif s == "g":
					row.append(GrassTile(self.main))
				elif s == "d":
					row.append(DirtFloorTile(self.main))
				elif s == "D":
					row.append(DirtWallTile(self.main))
				elif s == "W":
					row.append(WallTile(self.main))
				elif s == "P":
					row.append(PitTile(self.main))
				elif s == "E":
					row.append(SpawnerTile(self.main))
			grid.tiles.append(row)

		return grid

	def update(self):
		"""
		World.update - Called by Main.
		Updates all entities and handles/performs events.
		Dead entities are pruned in this function.
		"""
		for e in self.main.events:
			if not self.player.dead:
				if e.type == KEYDOWN and e.key == K_ESCAPE:
					self.paused = not self.paused
					self.play_sound("pause_sound", volume=0.5)
					if self.paused:
						self.main.music.set_volume(0.025)
					else:
						self.main.music.set_volume()
		if not self.paused or self.player.dead:
			#Updates the fade
			if self.fade != None:
				self.fade.update()
				if self.fade.dead:
					if self.player.dead:
						self.main.reset()
					else:
						self.fade = None
			else:
				#Death-screen fade-away.
				if self.player.dead:
					self.fade = FadeToBlack(self.main)
					self.fade.fade_length = 160


			if not self.player.dead:
				#Updates the script
				i = 0
				while i < len(self.scripts):
					self.scripts[i].parse_script()
					if self.scripts[i].dead:
						del self.scripts[i]
					else:
						i += 1

				#Manage Transitions
				if self.transition != None:
					self.transition.update()
					#Checks out the changed tiles.
					changes = []
					for change in self.transition.changed_tiles:
						if change[1].solid != change[2].solid or change[1].is_a_pit != change[2].is_a_pit:
							#we play a rumble sound for this tile.
							match = False
							for ch in changes:
								if ch[0] == change[0][0] and ch[1] == "tile_change":
									match = True
									break
							if not match:
								changes.append((change[0][0], "tile_change"))
						elif change[1].color != change[2].color:
							#we play a magical sound for this tile.
							match = False
							for ch in changes:
								if ch[0] == change[0][0] and ch[1] == "tile_change_color":
									match = True
									break
							if not match:
								changes.append((change[0][0], "tile_change_color"))
						if type(change[2]) == SpawnerTile:
							pos = ((change[0][0]+0.5)*TILE_SIZE, (change[0][1]+0.5)*TILE_SIZE)
							self.npcs.append(Baddie1(self.main, pos))
					if len(changes) > 0:
						volume = 1.0 / len(changes)
						for ch in changes:
							pos = ((ch[0]+0.5)*TILE_SIZE, 0) #the y doesn't matter.
							self.play_sound(ch[1], pos, volume)
					#Finally, we check if the transition has finished.
					if self.transition.done_transitioning:
						self.transition = None
					"""
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
				"""

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

	def move(self):
		"""
		World.move - Called by Main.
		Calls 'move' on all entities.
		"""
		if not self.paused or self.player.dead:
			self.player.move()
			if not self.player.dead:
				for npc in self.npcs:
					npc.move()
				for particle in self.particles:
					particle.move()

			# === MOVES THE 'CAMERA' ===
			#first we center it.
			new_offset = [float(self.preferred_offset[0]), float(self.preferred_offset[1])]
			if not self.disable_update_offset:
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

					new_offset = [new_offset[0]-offset[0],
									new_offset[1]-offset[1]]
			if self.earthquake_amount > 0:
				new_offset = [new_offset[0] + random.randint(-1,1) * self.earthquake_amount,
								new_offset[1] + random.randint(-1,1) * self.earthquake_amount]
			#finally, we apply the new offset.
			#new_offset = lerp_pos(self.visible_grid.offset, new_offset, 0.1)
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

		#we do letter-boxes for when the player doesn't have control.
		if self.player.controls_disabled:
			size = 75
			color = (127,127,127)
			self.main.screen.fill(color, (0,0,self.main.screen_size[0],size), special_flags=BLEND_RGB_MULT)
			self.main.screen.fill(color, (0,self.main.screen_size[1]-size,self.main.screen_size[0],size), special_flags=BLEND_RGB_MULT)

		if self.fade != None:
			self.fade.render()

		#We increment the current frame number.
		if not self.paused:
			self.current_frame += 1
