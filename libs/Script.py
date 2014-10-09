from TransitionSystem import *
from TileSystem import *

import string

DEBUG_PRINT_PARSE_SCRIPT = 1 #0 is off, 1 is just the comments, and 2 is everything.

class Script(object):
	def __init__(self, world, filename):
		self.world = world
		self.filename = filename

		self.script = self.load_script(filename)

		self.script_index = 0
		self.prev_script_index = -1
		self.dead = False

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

	def parse_script(self):
		running = True
		iterate = True
		while running:
			if self.script_index < len(self.script):
				line = self.script[self.script_index]
				if self.prev_script_index != self.script_index:
					if DEBUG_PRINT_PARSE_SCRIPT == 2 or (DEBUG_PRINT_PARSE_SCRIPT == 1 and line.startswith("#")):
						print self.filename+": "+line

				if line.startswith("#") or line == "":
					pass
				elif line.startswith("load_song "):
					song = line[len("load_song "):]
					self.world.main.music.load_music(song)
				elif line == "play_music":
					self.world.main.music.begin()
				elif line == "stop_music":
					self.world.main.music.stop()
				elif line.startswith("cue_music "):
					cued = line[len("cue_music "):]
					self.world.main.music.cue(int(cued))
				elif line.startswith("hard_cue_music "):
					cued = line[len("hard_cue_music "):]
					self.world.main.music.cue(int(cued), True)
				elif line.startswith("transition "):
					transition = line[len("transition "):]
					parts = transition.split(" ")
					grid_filename = parts[0]
					new_grid = self.world.load_grid(grid_filename)
					if parts[1] == "HintedTransition":
						args = parts[2:]
						if len(args) > 0:
							self.transition = eval("HintedTransition(self.main, self.grid, new_grid, self.visible_grid, "+string.join(args)+")")
						else:
							self.transition = HintedTransition(self.world.main, self.world.grid, new_grid, self.world.visible_grid)
					else:
						trans_type = eval(parts[1])
						length = int(parts[2])
						self.transition = trans_type(self.world.main, self.world.grid, new_grid, self.world.visible_grid, trans_len = length)
				elif line == "disable_player_controls":
					self.world.player.controls_disabled = True
					self.world.player.walking = False
				elif line == "enable_player_controls":
					self.world.player.controls_disabled = False
					self.world.player.walking = False
				elif line.startswith("set_player_direction "):
					self.world.player.direction = int(line[len("set_player_direction "):])
					self.world.player.set_sprite_direction()
					self.world.player.sprite.set_frame("walk1")
				elif line.startswith("set_player_walking "):
					self.world.player.walking = eval(line[len("set_player_walking "):])
				elif line.startswith("earthquake "):
					prev_quake = int(self.earthquake_amount)
					self.earthquake_amount = int(line[len("earthquake "):])
					if prev_quake <= 0 and self.earthquake_amount > 0:
						self.world.earthquake_sound_channel.play(self.world.earthquake_sound, -1)
					elif prev_quake > 0 and self.earthquake_amount <= 0:
						self.world.earthquake_sound_channel.stop()
					self.world.earthquake_sound_channel.set_volume(min(max(self.earthquake_amount*0.33,0.0),1.0))
				elif line.startswith("wait "):
					wait = line[len("wait "):]
					if wait.startswith("current_music "):
						music = int(wait[len("current_music "):])
						if self.world.main.music.current != music:
							iterate = False
							running = False
					elif wait.startswith("music_pos "):
						pos = float(wait[len("music_pos "):])
						if not (self.world.main.music.prev_sound_pos < pos and (self.world.main.music.sound_pos >= pos or self.world.main.music.sound_pos < self.world.main.music.prev_sound_pos)):
							iterate = False
							running = False
					elif wait.startswith("delay "):
						delay = long(wait[len("delay "):])
						self.world.main_script[self.world.main_script_index] = "wait frame "+str(self.world.current_frame + delay)
						iterate = False
						running = False
					elif wait.startswith("frame "):
						frame = long(wait[len("frame "):])
						if self.world.current_frame < frame:
							iterate = False
							running = False
					elif wait == "end_transition":
						if self.transition != None:
							iterate = False
							running = False
					elif wait == "enemies_dead":
						count = 0
						for npc in self.world.npcs:
							if npc.is_bad:
								count += 1
						if count != 0:
							iterate = False
							running = False
					elif wait == "trigger_tile":
						pos = round_coords((float(self.world.player.pos[0])/TILE_SIZE,float(self.world.player.pos[1])/TILE_SIZE))
						if self.world.grid.is_legal_coords(pos):
							tile = self.world.grid.tiles[pos[1]][pos[0]]
							if type(tile) != TriggerTile:
								iterate = False
								running = False
				if iterate:
					self.script_index += 1
			else:
				running = False
				self.dead = True

		self.prev_main_script_index = long(self.script_index)