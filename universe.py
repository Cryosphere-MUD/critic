import json

from musictypes import TypeSpecificMudObject

with open('../world.json') as world_json:
        UNIVERSE = json.load(world_json)
        world_json.close()

valid_quests = {}
valid_minis = {}
valid_sims = {}
valid_zonetags = set(("@auto", ))

UNIVERSE_BY_ID: dict[str, dict[str, int | str | list[str]]] = {}

UNIVERSE_BY_ID["@musicmud"] = dict(id="@musicmud")

TREATAS_USERS = {}

for obj in UNIVERSE:
        UNIVERSE_BY_ID[obj.get("id")] = obj
        #VALID_IDS.append(obj.get("id"))

        if zonetag := obj.get("zone"):
                valid_zonetags.add(zonetag)     

        if "Mission" in obj.get("flags"):
                valid_quests[obj.get("mname").upper()] = TypeSpecificMudObject(obj)

        if "MiniMission" in obj.get("flags"):
                valid_minis[obj.get("mname").upper()] = TypeSpecificMudObject(obj)

        if "Simulation" in obj.get("flags"):
                if obj.get("mname"):
                        valid_sims[obj.get("mname").upper()] = TypeSpecificMudObject(obj)

        if treatas := obj.get("treatas"):
                if treatas != obj.get("id"):
                        TREATAS_USERS.setdefault(treatas, []).append(obj)
