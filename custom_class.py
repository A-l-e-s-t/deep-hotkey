class Custom:
	def __init__(self):
		pass

	def __setattr__(self, name, value):
		self.__dict__[name] = value
