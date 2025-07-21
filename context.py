from luatypes import TypeAny, TypeString, TypeTable
from mudtypes import TypeMudObject
from mudversion import is_aardmud
from bindingsparser import struct_types

def get_default_context():
        if is_aardmud:
                return {"ch": struct_types.get("ch"),
                           "self": struct_types.get("ch"),
                           "obj": struct_types.get("obj"),
                           "room": struct_types.get("room"),
                           "mud": struct_types.get("mud")
                           }
                
        return {"o1": TypeMudObject(),
                "o2": TypeAny(),
                "o3": TypeAny(),
                "pl": TypeMudObject(invoker=True),
                "txt": TypeString(tainted=True),
                "arg": TypeTable(value=TypeString(tainted=True))}

def in_global(ckey):
        if ckey in ["o1", "pl", "o2", "o3", "event", "txt", "arg", "treatas"]:
                return True
        return False
