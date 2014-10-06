class Entity(object):
	"""
	The parent class for all entities.
	"""
	def __init__(self, main, pos):
		self.main = main
		self.pos = pos
		self.dead = False
		self.init()

	def init(self):
		"""
		It may seem silly, but this is here so that the child-class
		can do it's own initializing after the parent is done.
		"""
		pass

	def update(self):
		pass

	def move(self):
		pass

	def flag_for_rerender(self):
		self.flagged_for_rerender = True

	def rerender(self):
		pass

	def render(self):
		pass

