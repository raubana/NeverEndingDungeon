import pygame

from TransitionSystem import *
from TileSystem import *
from FadeSystem import *

import string

DEBUG_PRINT_PARSE_SCRIPT = 0 #0 is off, 1 is just the comments, and 2 is everything.

class Script(object):
	def __init__(self, world, filename):
		self.world = world
		self.filename = filename

		self.set_script(filename)

	def set_script(self, filename):
		self.script = self.load_script(filename)
		self.filename = filename
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
		if self.dead:
			return

		running = True
		while running:
			running = True
			iterate = True
			if self.script_index < len(self.script):
				line = self.script[self.script_index]
				if self.prev_script_index != self.script_index:
					if DEBUG_PRINT_PARSE_SCRIPT == 2 or (DEBUG_PRINT_PARSE_SCRIPT == 1 and line.startswith("#")):
						print self.filename+": "+line

				if line.startswith("#") or line == "":
					pass
				elif line == "autosave":
					self.world.autosave()
				elif line == "quit":
					self.world.main.running = False
				elif line.startswith("add_script "):
					script_name = line[len("add_script "):]
					self.world.scripts.append(Script(self.world, script_name))
				elif line.startswith("kill_script "):
					worked = False
					script_name = line[len("kill_script "):]
					i = 0
					while i < len(self.world.scripts):
						if self.world.scripts[i].filename == script_name:
							del self.world.scripts[i]
						else:
							i += 1
					if not worked and DEBUG_PRINT_PARSE_SCRIPT > 0:
						print "ERROR: called 'kill_script' for '"+script_name+"' but it doesn't exist."
				elif line.startswith("load_script "):
					script_name = line[len("load_script "):]
					self.set_script(script_name)
					iterate = False
				elif line.startswith("set_main_script "):
					script_name = line[len("set_main_script "):]
					if len(self.world.scripts) == 0:
						self.world.scripts.append(Script(self.world,script_name))
					else:
						self.world.scripts[0].set_script(script_name)
						if self.world.scripts[0] == self:
							iterate = False
				elif line.startswith("set_script_index "):
					worked = False
					parts = line[len("set_main_script "):].strip().split(" ")
					script_name = parts[0]
					index = int(parts[1])
					for script in self.world.scripts:
						if script.filename == script_name:
							script.set_script(script_name) #This is here in case the script has self-modified.
							script.script_index = index
							worked = True
					if script_name == self.filename:
						iterate = False
						running = False #For debugging only. However, it does seem to fix the infinite-loop bug.
					if not worked and DEBUG_PRINT_PARSE_SCRIPT > 0:
						print "ERROR: called 'set_script_index' for '"+script_name+"' but it doesn't exist."
				elif line.startswith("load_music "):
					song = line[len("load_music "):]
					self.world.main.music.load_music(song)
				elif line.startswith("play_music"):
					if line == "play_music":
						self.world.main.music.begin()
					else:
						part = int(line[len("play_music "):])
						self.world.main.music.begin(part)
				elif line == "stop_music":
					self.world.main.music.stop()
				elif line.startswith("cue_music "):
					cued = line[len("cue_music "):]
					self.world.main.music.cue(int(cued))
				elif line.startswith("hard_cue_music "):
					cued = line[len("hard_cue_music "):]
					self.world.main.music.cue(int(cued), True)
				elif line.startswith("play_sound "):
					play = line[len("play_sound "):]
					parts = play.split(" ")
					sound_name = parts[0]
					volume = float(parts[1])
					self.world.play_sound(sound_name, volume = volume)
				elif line.startswith("set_fade "):
					self.world.fade = eval(line[len("set_fade "):]+"(self.world.main)")
				elif line == "force_full_rerender":
					self.world.visible_grid.flag_for_rerender()
					self.world.visible_grid.force_full_rerender = True
				elif line.startswith("set_grid "):
					grid_filename = line[len("set_grid "):]
					self.world.transition = None
					self.world.grid = self.world.load_grid(grid_filename)
				elif line.startswith("transition "):
					transition = line[len("transition "):]
					parts = transition.split(" ")
					grid_filename = parts[0]
					new_grid = self.world.load_grid(grid_filename)
					if parts[1] == "HintedTransition":
						args = parts[2:]
						if len(args) > 0:
							self.world.transition = eval("HintedTransition(self.world.main, self.world.grid, new_grid, self.world.visible_grid, "+string.join(args)+")")
						else:
							self.world.transition = HintedTransition(self.world.main, self.world.grid, new_grid, self.world.visible_grid)
					else:
						trans_type = eval(parts[1])
						length = int(parts[2])
						self.world.transition = trans_type(self.world.main, self.world.grid, new_grid, self.world.visible_grid, trans_len = length)
				elif line == "disable_update_offset":
					self.world.disable_update_offset = True
				elif line == "enable_update_offset":
					self.world.disable_update_offset = False
				elif line.startswith("set_offset "):
					offset = eval(line[len("set_offset "):])
					self.world.current_offset = offset
				elif line.startswith("set_preferred_offset "):
					offset = eval(line[len("set_preferred_offset "):])
					self.world.preferred_offset = offset
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
				elif line.startswith("set_player_pos "):
					pos = eval(line[len("set_player_pos "):])
					self.world.player.pos = pos
				elif line.startswith("set_player_thought "):
					thought = line[len("set_player_thought "):]
					self.world.player.thought_sprite.set_frame(thought)
				elif line.startswith("earthquake "):
					prev_quake = int(self.world.earthquake_amount)
					self.world.earthquake_amount = int(line[len("earthquake "):])
					if prev_quake <= 0 and self.world.earthquake_amount > 0:
						self.world.earthquake_sound_channel.play(self.world.earthquake_sound, -1)
					elif prev_quake > 0 and self.world.earthquake_amount <= 0:
						self.world.earthquake_sound_channel.stop()
					self.world.earthquake_sound_channel.set_volume(min(max(self.world.earthquake_amount*0.25,0.0),1.0))
				elif line == "start_newgame":
					self.world.start_new_game()
				elif line == "continue_saved_game":
					self.world.continue_saved_game()
				elif line.startswith("wait "):
					iterate = False
					running = False

					wait = line[len("wait "):]
					if wait.startswith("current_music "):
						music = int(wait[len("current_music "):])
						if self.world.main.music.current == music:
							iterate = True
							running = True
					elif wait.startswith("music_pos "):
						pos = float(wait[len("music_pos "):])
						if self.world.main.music.prev_sound_pos < pos and (self.world.main.music.sound_pos >= pos or self.world.main.music.sound_pos < self.world.main.music.prev_sound_pos):
							iterate = True
							running = True
					elif wait.startswith("music_beat "):
						beat = int(wait[len("music_beat "):])
						if self.world.main.music.beat == beat and (self.world.main.music.beat != self.world.main.music.prev_beat):
							iterate = True
							running = True
					elif wait.startswith("delay "):
						delay = long(wait[len("delay "):])
						self.script[self.script_index] = "wait frame "+str(self.world.current_frame + delay)
						running = True
					elif wait.startswith("frame "):
						frame = long(wait[len("frame "):])
						if self.world.current_frame >= frame:
							iterate = True
							running = True
					elif wait == "end_transition":
						if self.world.transition == None:
							iterate = True
							running = True
					elif wait == "end_fade":
						if self.world.fade == None or self.world.fade.dead:
							iterate = True
							running = True
					elif wait == "enemies_dead":
						count = 0
						for npc in self.world.npcs:
							if npc.is_bad:
								count += 1
						if count == 0:
							iterate = True
							running = True
					elif wait.startswith("trigger_tile ") or wait.startswith("trigger_tile_touch "):
						if wait.startswith("trigger_tile "):
							trigger = "trigger_tile"
							tile_id = wait[len("trigger_tile "):]
						else:
							trigger = "trigger_tile_touch"
							tile_id = wait[len("trigger_tile_touch "):]
						tile_id = tile_id.strip()
						pos = round_coords((float(self.world.player.pos[0])/TILE_SIZE,float(self.world.player.pos[1])/TILE_SIZE))
						if self.world.grid.is_legal_coords(pos):
							tile = self.world.grid.tiles[pos[1]][pos[0]]
							if type(tile) == TriggerTile:
								if tile_id == "" or tile.id == tile_id:
									if trigger == "trigger_tile_touch":
										iterate = True
										running = True
									else:
										rect = pygame.Rect([pos[0]*TILE_SIZE,pos[1]*TILE_SIZE,TILE_SIZE,TILE_SIZE])
										if rect.contains(self.world.player.rect):
											iterate = True
											running = True
					else:
						print "UNKNOWN WAIT TYPE:",line
				else:
					print "UNKNOWN SCRIPT COMMAND:",line
				if iterate:
					self.script_index += 1
			else:
				if DEBUG_PRINT_PARSE_SCRIPT == 2:
						print self.filename+": REACHED EOF."
				running = False
				self.dead = True

		self.prev_script_index = long(self.script_index)