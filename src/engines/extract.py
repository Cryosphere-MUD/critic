#!/usr/bin/python3

def get_world():

	f = open("src/engines/asteriamud/zones/asteria/rooms")

	objects = []
	trigger_text = False

	try:
		obj = None

		while True:
			line = next(f)

			line = line[:-1]

			if line == '@':
				obj["lua.trigger"] = trigger_buffer
				trigger_text = False
				trigger_buffer = ""
				continue

			if trigger_text:
				trigger_buffer += line

			if line.startswith('\t'):
				line = line.strip()
				if line == "EXIT":
					exit_block = True
					continue
				if line == "END":
					exit_block = False
					continue

				key, value = line.split(" ", 1)
				obj[key] = value
				if line.startswith("TRIGGER "):
					trigger = True
				if line.startswith("TEXT "):
					trigger_buffer = ""
					trigger_text = True
				line = line[5:]

			if line.startswith("ID "):
				obj = {}
				obj["id"] = line[3:]
				obj["flags"] = []
				continue

			if line.startswith("END"):
				objects.append(obj)
				continue

	except StopIteration as e:
		pass

	return objects

UNIVERSE_BY_ID = get_world()
