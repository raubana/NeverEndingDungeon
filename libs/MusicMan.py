import pygame

import time

class MusicMan(object):
	def __init__(self, main):
		self.main = main

		self.intro_loop = None
		self.intro_loop_beats = 0
		self.intro_trans = None
		self.intro_trans_beats = 0
		self.main_loop = None
		self.main_loop_beats = 0
		self.main_loop_quiet = None
		self.main_loop_quiet_beats = 0

		self.bpm = 0
		self.sound_start = 0
		self.sound_length = 0
		self.sound_pos = 0
		self.prev_sound_pos = 0

		self.current = None
		self.cued = None #0 intro, 1 intro to main, 2 main, 3 main (quiet)
		self.synced = True

		self.volume = 0.4

	def load_music(self, song):
		f = open("snds/songs/"+song+"/bpm.txt")
		self.bpm = float(f.readline())
		self.intro_loop_beats = float(f.readline())
		self.intro_trans_beats = float(f.readline())
		self.main_loop_beats = float(f.readline())
		self.main_loop_quiet_beats = float(f.readline())

		self.songname = song

	def cue(self, part, force=False):
		self.cued = part
		self.synced = not force

	def get_current_soundname(self):
		if self.current == 0: return "snds/songs/"+self.songname+"/"+self.songname+"_intro_loop.ogg"
		elif self.current == 1: return "snds/songs/"+self.songname+"/"+self.songname+"_intro_to_main.ogg"
		elif self.current == 2: return "snds/songs/"+self.songname+"/"+self.songname+"_main_loop.ogg"
		elif self.current == 3: return "snds/songs/"+self.songname+"/"+self.songname+"_main_quiet_loop.ogg"

	def begin(self):
		self.current = 0
		self.cued = None
		pygame.mixer.music.load(self.get_current_soundname())
		pygame.mixer.music.play(-1)
		self.sound_start = time.time()
		pygame.mixer.music.set_volume(self.volume)

		self.prev_beat = 0.0

	def stop(self):
		pygame.mixer.music.stop()
		self.current = None

	def update(self):
		if self.current != None:
			dif = (time.time() - self.sound_start) * (self.bpm/60.0)
			if self.current == 0: self.sound_pos = dif % (self.intro_loop_beats)
			elif self.current == 1: self.sound_pos = dif % (self.intro_trans_beats)
			elif self.current == 2: self.sound_pos = dif % (self.main_loop_beats)
			elif self.current == 3: self.sound_pos = dif % (self.main_loop_quiet_beats)

			self.beat = self.sound_pos % 4
			if self.cued != self.current and self.cued != None:
				if int(self.beat) != int(self.prev_beat):
					play_next = False
					if self.synced:
						if (self.current == 0 and self.cued == 1):
							if self.prev_beat > self.beat:
								play_next = True
						elif self.current == 1:
							if self.prev_sound_pos > self.sound_pos:
								play_next = True
						elif self.current in (2,3):
							if self.prev_beat > self.beat:
								play_next = True
					else:
						play_next = True
					if play_next:
						self.current = int(self.cued)
						if self.current == 1:
							self.cued = 2
						else:
							self.cued = None
						pygame.mixer.music.load(self.get_current_soundname())
						pygame.mixer.music.play(-1, (60.0/self.bpm)*self.sound_pos)
						self.sound_start = time.time()-(60.0/self.bpm)*self.sound_pos
						pygame.mixer.music.set_volume(self.volume)

			self.prev_beat = float(self.beat)
			self.prev_sound_pos = float(self.sound_pos)