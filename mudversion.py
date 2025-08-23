import json

config = None

config_file = ".critic.config"

def get_config():
        global config
        if config_file is None:
                return {}

        if config is None:
                try:
                        with open(config_file) as verbs_json:
                                config = json.load(verbs_json)
                except FileNotFoundError:
                        config = {}
                
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

def get_intrinsic_zones():
        return get_config().get("zones", ())

def is_musicmud():
        return get_config().get("musicmud")

def is_aardmud():
        return get_config().get("aardmud")