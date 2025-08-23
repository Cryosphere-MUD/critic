from luatypes import TypeNumber, CapitalsModule, TypeAny, TypeFunction, TypeFunctionAny, TypeString, TypeBool
from mudtypes import TypeMudObjectOrID
from universe import valid_quests, valid_minis, valid_sims

from mudversion import get_flags_path, get_pflags_path

def register_mud_global_scope(global_scope):

        valid_flags = {}

        if flagname := get_flags_path():
                with open(flagname, "r") as file:
                        for idx, f in enumerate(file):
                                valid_flags[f.strip().split(" ")[0].upper()] = TypeNumber(idx + 1)

        valid_pflags = {}

        if pflagname := get_pflags_path():
                with open(pflagname, "r") as file:
                        for idx, f in enumerate(file):
                                valid_pflags[f.strip().split(" ")[0].upper()] = TypeNumber(idx + 1)

        UNCHECKED_MODULES = []
        UNCHECKED_MODULES.append("coroutine")
        UNCHECKED_MODULES.append("trace")
        UNCHECKED_MODULES.append("coroutines")
        UNCHECKED_MODULES.append("json")
        UNCHECKED_MODULES.append("Array")
        UNCHECKED_MODULES.append("attributes")
        UNCHECKED_MODULES.append("json")
        UNCHECKED_MODULES.append("match") # matcher bitflags

        for module in UNCHECKED_MODULES:
                global_scope[module] = TypeAny()

        global_scope["priv"] = CapitalsModule(valid_pflags)
        global_scope["flag"] = CapitalsModule(valid_flags)

        global_scope["quest"] = CapitalsModule(valid_quests)
        global_scope["mini"] = CapitalsModule(valid_minis)
        global_scope["sim"] = CapitalsModule(valid_sims)

        global_scope["stance"] = CapitalsModule("STANDING", "SITTING", "LYING", "SWIMMING", "FLYING")

        global_scope["rank"] = CapitalsModule("POfficer", "Crewman", "commander", "Captain", "Commodore")
        
        # global_scope["util"].add("explode", TypeAny())
        # global_scope["util"].add(TypeFunction(name="colour_reverse", args=[TypeString()], return_type=TypeString()))
        # global_scope["util"].add("colour_trim", TypeAny())
        # global_scope["util"].add("formatitime", TypeAny())

        # global_scope["cash"].add("match", TypeAny())

        # global_scope["mud"].add("planet_objects", TypeFunctionAny(name="planet_objects"))
        # global_scope["mud"].add("is_planet", TypeFunctionAny(name="is_planet"))

        # global_scope["lock"] = TypeFunction(name="lock", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        # global_scope["open"] = TypeFunction(name="open", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        # global_scope["close"] = TypeFunction(name="close", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        # global_scope["pressurise"] = TypeFunction(name="pressurise", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        # global_scope["depressurise"] = TypeFunction(name="depressurise", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)

        # global_scope["plural"] = TypeFunction(name="plural", args=[TypeAny()], return_type=TypeBool())

        global_scope["error"] = TypeFunction(name="error", args=[TypeString()], min_args=0, no_return=True)

        GLOBAL_SYMBOLS = ("import", "sendrg", "check_syntax",
                          "rawget", "get_max_opcount", "get_opcount", "proxy_table", "get_route", "clone")

        for symbol in GLOBAL_SYMBOLS:
                global_scope[symbol] = TypeFunctionAny(name=symbol)
                global_scope[symbol].is_global = True


