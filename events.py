import os, sys

from luatypes import TypeString, TypeNil, TypeNil, TypeUnion, TypeTable, TypeNumber, TypeBool, TypeAny, TypeNumberRange
from mudtypes import TypeMudObject

from mudversion import has_events

def arg_from_type(type):
        if "|" in type:
                types = [arg_from_type(part.strip()) for part in type.split("|")]
                return TypeUnion(*types)

        if type == "int | string":
                return TypeUnion(TypeString(), TypeNumber())
        elif type == "string":
                return TypeString()
        elif type == "int":
                return TypeNumber()
        elif type == "nil":
                return TypeNil()
        elif type == "any":
                return TypeAny()
        elif type == "bool":
                return TypeBool()
        elif type == "objset":
                return TypeTable(value=TypeMudObject())
        elif type == "objvec":
                return TypeTable(value=TypeMudObject())
        elif type == "table":
                return TypeTable()
        elif type == "mudobject":
                return TypeMudObject()
        elif type.isdigit():
                return TypeNumberRange(int(type))
        else:
                print("unknown type!", type)
                exit(1)

def arg_type(s):
        if s.name == "arg":
                type = TypeTable(value=TypeString(tainted=True))
        elif s.name == "txt":
                type = TypeString(tainted=True)
        elif s.name == "pl":
                type = TypeMudObject(invoker=True)
        else:
                type = arg_from_type(s.type)
        
        if s.optional:
                return TypeUnion(TypeNil(), type)
        
        if type == TypeString:
                return type(tainted=True)

        return type

class MudEvent:
        def __init__(self, event_args, return_type, const):
                self._args = {}

                for arg in event_args:
                        self._args[arg.name] = arg_type(arg)

                if return_type:
                        self.return_type = [arg_type(t) for t in return_type]
                else:
                        self.return_type = None

                self.const = const

        def items(self):
                yield from self._args.items()

        def keys(self):
                yield from self._args.keys()

        def values(self):
                yield from self._args.values()

valid_events: dict[str, bool | list[str]] = {}

if has_events():

        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from lib import events

        for event in events.parse_events():
                event_name = event.name

                event_args = event.params

                if event_args is None:
                        valid_events[event_name] = True
                        continue

                valid_events[event_name] = MudEvent(event_args, event.return_type, event.const)


def check_valid_action(verb):
        from functions import VERBS
        return VERBS.get(verb) is not None


def check_valid_event(event):
        if event.startswith(prefix := "lua."):
                event = event[len(prefix):]

        if event in valid_events:
                return valid_events.get(event)

        if "." in event:
                ev = event.split(".")[0] + ".*"
                if ev in valid_events:
                        return valid_events.get(ev)