from luatypes import TypeNumber, CapitalsModule, TypeAny, TypeFunction, TypeFunctionAny, TypeString, TypeBool
from mudtypes import TypeMudObjectOrID
from universe import valid_quests, valid_minis, valid_sims

from mudversion import get_flag_modules

def register_mud_global_scope(global_scope):

        for module, filename in get_flag_modules().items():
                valid_flags = {}
                with open(filename, "r") as file:
                        for idx, f in enumerate(file):
                                valid_flags[f.strip().split(" ")[0].upper()] = TypeNumber(idx + 1)

                global_scope[module] = CapitalsModule(valid_flags)
                
        UNCHECKED_MODULES = []
        UNCHECKED_MODULES.append("coroutine")
        UNCHECKED_MODULES.append("trace")
        UNCHECKED_MODULES.append("json")
        UNCHECKED_MODULES.append("Array")

        for module in UNCHECKED_MODULES:
                global_scope[module] = TypeAny()

        global_scope["quest"] = CapitalsModule(valid_quests)
        global_scope["mini"] = CapitalsModule(valid_minis)
        global_scope["sim"] = CapitalsModule(valid_sims)

        global_scope["rank"] = CapitalsModule("POfficer", "Crewman", "commander", "Captain", "Commodore")
