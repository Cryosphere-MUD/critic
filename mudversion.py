import json

config = {}

config_file = None

def set_config(file):
	global config_file
	config_file = file

def get_config():
	global config
	if config_file is None:
		return {}
	
	if config is None:
		with open(config_file) as verbs_json:
	        	config = json.load(verbs_json)
		
	return config

def get_bindings_glob():
	return get_config().get("bindings", "")

def get_world_path():
	return get_config().get("world")

def get_flags_path():
	return get_config().get("flags")

def get_pflags_path():
	return get_config().get("pflags")

def has_events():
	return get_config().get("events")