import typing

from context import default_context, in_global
from errors import error, set_filename
from events import MudEvent, check_valid_event
from luatypes import TypeMap, TypeUnion, TypeAny
from mudtypes import TypeSpecificMudObject
from universe import UNIVERSE_BY_ID, TREATAS_USERS
from chunkvalidate import validate_chunk

def get_context_and_return_type(args, item, itemid, key, chunkpart):
	context = dict(default_context)

	event_validity = check_valid_event(chunkpart)

	return_type = None

	if not event_validity:
		if args.unknown:
			error(f"unknown event {chunkpart}")
	elif isinstance(event_validity, dict):
		context = event_validity
	elif isinstance(event_validity, MudEvent):
		for event_arg, event_value in event_validity.items():
			context[event_arg] = event_value
		return_type = event_validity.return_type

	if itemid and itemid not in TREATAS_USERS:
		context["o1"] = TypeSpecificMudObject(item)
	else:
		specifics = list(TypeSpecificMudObject(obj) for obj in TREATAS_USERS[itemid])
		context["o1"] = TypeUnion(*specifics)

	context["event"] = TypeMap(context)

	context = {ckey : cvalue for ckey, cvalue in context.items() if in_global(ckey)}

	return context, return_type

def check_world(UNIVERSE_BY_ID, args, ZONE):

	for itemid, item in UNIVERSE_BY_ID.items():

		itemid = item.get("id")

		if args.world and itemid.startswith("%"):
			continue

		# if itemid in SKIP:
		# 	continue

		# if ONLY and itemid not in ONLY:
		# 	continue

		zone = item.get("zone", "")

		if ZONE and zone not in ZONE and itemid not in ZONE:
			continue
		
		zoneobj = UNIVERSE_BY_ID.get("mini_" + zone)
		
		if not zoneobj:
			zoneobj = UNIVERSE_BY_ID.get(zone + "_zone")

		flags: list[str] = []
		if zoneobj and zoneobj.get("flags"):
			flags = typing.cast(list[str], zoneobj.get("flags"))

		no_detailed = "Private" in flags or "Personal" in flags

		if args.resolution_only:
				no_detailed = True

		for key, value in item.items():
			if key.startswith("lua."):

				if item.get("critic.ignore." + key):
					continue

				if value[0] == '>':
					continue

				rewrite_warning_disabled = itemid.startswith("%verb_")

				chunkpart = key[4:]

				set_filename(itemid + "." + key)

				context, return_type = get_context_and_return_type(args, item, itemid, key, chunkpart)

				file = itemid + "." + key

				try:
					validate_chunk(value, context, rewrite_warning_disabled, itemid, no_detailed = no_detailed, return_type = return_type)
				except KeyboardInterrupt:
					print("interrupting")
					exit(1)
					raise
				except:
					import traceback
					traceback.print_exc()
					error("unknown error")
					raise

