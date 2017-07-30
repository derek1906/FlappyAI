class EventManager:
	'''
	Generic event manager
	'''
	def __init__(self):
		self.events = {}

	def add(self, event_name, callback):
		if event_name not in self.events:
			self.events[event_name] = []
		self.events[event_name].append(callback)

	def trigger(self, event_name, *values):
		if event_name in self.events:
			for callback in self.events[event_name]:
				callback(event_name, *values)