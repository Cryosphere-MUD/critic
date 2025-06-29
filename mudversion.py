import json

res = {}

with open('../.critic.config') as verbs_json:
        res = json.load(verbs_json)

def get_bindings_glob():
	return res.get("bindings")