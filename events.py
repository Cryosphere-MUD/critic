import os, sys

from musictypes import TypeString, TypeMudObject, TypeNil, TypeUnion, TypeTable, TypeNumber, TypeBool, TypeAny

valid_events: dict[str, bool | list[str]] = {}

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import events

def arg_type(s):
        if s.name == "arg":
                type = TypeTable(value=TypeString(tainted=True))
        elif s.name == "txt":
                type = TypeString(tainted=True)
        elif s.name == "pl":
                type = TypeMudObject(invoker=True)
        elif s.type == "int | string":
                type = TypeUnion(TypeString(), TypeNumber())
        elif s.type == "string":
                type = TypeString()
        elif s.type == "int":
                type = TypeNumber()
        elif s.type == "any":
                type = TypeAny()
        elif s.type == "bool":
                type = TypeBool()
        elif s.type == "mudobject":
                type = TypeMudObject()
        else:
                print("unknown type!", s.type)
                exit(1)

        if s.optional:
                return TypeUnion(TypeNil(), type)
        
        if type == TypeString:
                return type(tainted=True)

        return type

class MudEvent:
        def __init__(self, event_args, return_type):
                self._args = {}

                for arg in event_args:
                        self._args[arg.name] = arg_type(arg)

                if return_type:
                        self.return_type = [arg_type(t) for t in return_type]
                else:
                        self.return_type = None

        def items(self):
                yield from self._args.items()

for event in events.parse_events():
        event_name = event.name

        event_args = event.params

        if event_args is None:
                valid_events[event_name] = True
                continue

        valid_events[event_name] = MudEvent(event_args, event.return_type)

valid_event_prefixes = {"tell.": True, "checklist.": True, "trap.": True, "lib": True, "verb.": True, "schema": True, "primitives": True, "helpers": True}


def check_valid_action(verb):
        from functions import VERBS
        return VERBS.get(verb) is not None


def check_valid_event(event):
        if event.startswith(prefix := "lua."):
                event = event[len(prefix):]

        if event in valid_events:
                return valid_events.get(event)

        if any(event.startswith(prefix) for prefix in valid_event_prefixes):
                return True
        
        if "." in event:
                ev = event.split(".")[0] + ".*"
                if ev in valid_events:
                        return valid_events.get(ev)