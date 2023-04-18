################################################################
# Multi Keypad
################################################################

from adafruit_ticks import ticks_ms, ticks_less

class Event:
	def __init__(self, keypad, event):
		self.pad_number = keypad
		self.timestamp = event.timestamp
		self.pressed = event.pressed
		self.released = event.released
		self.key_number = event.key_number
	def __repr__(self):
		status = "pressed" if self.pressed else "released"
		return f"<Event: pad_number {self.pad_number} key_number {self.key_number} {status}>"

class MultiKeypad:
	def __init__(self, *keypads):
		self.keypads = keypads
		self.events = [None] * len(keypads)

	def next_event(self):
		event = None
		for index, keypad in enumerate(self.keypads):
			if self.events[index] == None:
				nev = keypad.events.get()
				if nev:
					self.events[index] = (nev.timestamp, index, nev)
		if any(self.events):
			for evt in self.events:
				if evt is None:
					continue
				if (event is None) or (ticks_less(evt[0], event[0])):
					event = evt
			self.events[event[1]] = None
			return Event(event[1], event[2])
		return None
