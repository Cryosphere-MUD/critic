from luatypes import TypeAny, TypeString, TypeTable
from mudtypes import TypeMudObject
from mudversion import is_aardmud

default_context = {"o1": TypeMudObject(),
                "o2": TypeAny(),
                "o3": TypeAny(),
                "pl": TypeMudObject(invoker=True),
                "txt": TypeString(tainted=True),
                "arg": TypeTable(value=TypeString(tainted=True))}

if is_aardmud:
        default_context = {"ch": TypeMudObject(),
                           "self": TypeMudObject(),
                           "obj": TypeMudObject(),
                           "room": TypeMudObject(),
                           "mud": TypeMudObject()
                           }

def in_global(ckey):
        if ckey in ["o1", "pl", "o2", "o3", "event", "txt", "arg", "treatas"]:
                return True
        return False
