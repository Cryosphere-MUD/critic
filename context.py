from musictypes import TypeMudObject, TypeAny, TypeString, TypeTable

default_context = {"o1": TypeMudObject(),
                                   "o2": TypeAny(),
                                   "o3": TypeAny(),
                                   "pl": TypeMudObject(invoker=True),
                                   "txt": TypeString(tainted=True),
                                   "arg": TypeTable(value=TypeString(tainted=True))}

def in_global(ckey):
        if ckey in ["o1", "pl", "o2", "o3", "event", "txt", "arg", "treatas"]:
                return True
        return False
