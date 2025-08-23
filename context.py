from luatypes import TypeAny, TypeString, TypeTable
from mudtypes import TypeMudObject
from bindingsparser import struct_types, global_symbols

def get_default_context():
        if global_symbols:
                return global_symbols

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
