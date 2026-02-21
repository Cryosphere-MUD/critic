import json
from types import MappingProxyType

from mudtypes import TypeSpecificMudObject
from mudversion import get_world_path, get_intrinsic_zones
from engines import extract

def load_universe():
        UNIVERSE = extract.get_world()


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

valid_quests = {}
valid_minis = {}
valid_sims = {}
valid_zonetags = set(get_intrinsic_zones())

UNIVERSE_BY_ID: dict[str, dict[str, int | str | list[str]]] = {}

UNIVERSE_BY_ID["@musicmud"] = dict(id="@musicmud")

TREATAS_USERS = {}

if get_world_path() is not None:

        load_universe()

        UNIVERSE_BY_ID = MappingProxyType(UNIVERSE_BY_ID)

