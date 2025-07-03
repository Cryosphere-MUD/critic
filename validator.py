#!/usr/bin/env python3.11

import sys, typing, argparse
import glob
from luaparser import ast
from bindingsparser import parse_bindings
from musictypes import TypeSpecificMudObject, TypeUnion, TypeMudObject, TypeString, TypeAny, TypeTable, TypeMap
from visitor import MusicLUAVisitor
from environment import make_global_scope
from universe import UNIVERSE, UNIVERSE_BY_ID, TREATAS_USERS
from events import MudEvent, check_valid_event
from symbolresolver import resolve_symbols
import parents
from validatorstate import ValidatorState
from types import MappingProxyType
from mudversion import get_bindings_glob

SKIP: list[str] = []

#SKIP = ("system_lua_parser", )
#VALID_IDS = ["@musicmud"]

CLASS_METHODS = {}
MODULE_SYMBOLS = {}
BINDINGS = {}

import pprint

for binding_filename in glob.glob(get_bindings_glob()):
        with open(binding_filename, "r") as file:
                bindings, modules, klass = parse_bindings(file)
                BINDINGS.update(bindings)		
                MODULE_SYMBOLS.update(modules)
                
                for classname, methods in klass.items():
                        CLASS_METHODS.setdefault(classname, {}).update(methods)
                

got_error = False

errored_nodes = set()
error_fn = None

no_warnings = False

def error(txt, node = None, level = "error", line = None):

        if no_warnings and level == "warning":
                return

        if node:
                node = id(node)

        if node and node in errored_nodes:
                return

        if node:
                errored_nodes.add(node)

        fn_display = error_fn

        print(f"::{level}:: {fn_display} : {txt}", file=sys.stderr)

        if line:
                print(line)

        global got_error
        got_error = True

default_context = {"o1": TypeMudObject(),
                                   "o2": TypeAny(),
                                   "o3": TypeAny(),
                                   "pl": TypeMudObject(invoker=True),
                                   "txt": TypeString(tainted=True),
                                   "arg": TypeTable(value=TypeString(tainted=True))}

def validate_chunk(lua, context = None, rewrite_warning_disabled = False, itemid = None, no_detailed = False, return_type = None):

        if context is None:
                context = dict(default_context)

        global errored_nodes
        errored_nodes = set()

        if lua[0] == '#':
                return

        try:
                tree = ast.parse(lua)
#                print(ast.to_pretty_str(tree))
        except KeyboardInterrupt as e:
                raise
        except:
                error(f"failed parsing")
                return

        bindings_global = BINDINGS
        BINDINGS.update(MODULE_SYMBOLS)

        global_scope = make_global_scope(bindings_global)

        state = ValidatorState()
        state.parents = parents.get_parents(tree)
        state.context = context
        state.globals = MappingProxyType(global_scope)
        state.source = lua
        state.error_handler = error
        state.class_methods = CLASS_METHODS
        state.object_id = itemid
        state.expected_return_type = return_type

        state.resolutions, state.scopes = resolve_symbols(tree, state)

        if not no_detailed:

                v = MusicLUAVisitor(universe=UNIVERSE_BY_ID,
                                    state=state)
        
                v.visit(tree)

ONLY: list[str] = []

#ONLY = ("template_customsofficer_1")

#ONLY = ("wstone_pipe_1")

CHUNKS = []

ZONE = []

parser = argparse.ArgumentParser()
parser.add_argument("--spellcheck", help="Enable spellchecking mode", action="store_true")
parser.add_argument("--world", help="Only validate the world, no verbs", action="store_true")
parser.add_argument("--unknown", help="Errors for unknown events", action="store_true")
parser.add_argument("--no-warnings", help="Disable warnings", action="store_true")
parser.add_argument("--resolution-only", help="Only do symbol resolution", action="store_true")
parser.add_argument("objects", nargs="*", help="Objects or a file to test")

args = parser.parse_args()

if args.no_warnings:
        no_warnings = True

import spellcheck
if args.spellcheck:
        spellcheck.enable()
else:
        spellcheck.disable()

for arg in args.objects:
        try:
                file = open(arg, "r")
                CHUNKS.append(file.read())
        except:
                ZONE.append(arg)

if CHUNKS:
        for chunk in CHUNKS:
                validate_chunk(chunk)
        if got_error:
                print("there were errors")
                exit(1)
        else:
                print("all ok")
                exit(0)

def in_global(ckey):
        if ckey in ["o1", "pl", "o2", "o3", "event", "txt", "arg", "treatas"]:
                return True
        return False

for item in UNIVERSE:

        itemid = item.get("id")

        if args.world and itemid.startswith("%"):
                continue

        if itemid in SKIP:
                continue

        if ONLY and itemid not in ONLY:
                continue

        zone = item.get("zone", "")

        if ZONE and zone not in ZONE and itemid not in ZONE:
                continue
        
        zoneobj = UNIVERSE_BY_ID.get("mini_" + zone)
        
        if not zoneobj:
                zoneobj = UNIVERSE_BY_ID.get(zone + "_zone")

        flags: list[str] = []
        if zoneobj and zoneobj.get("flags"):
                flags = typing.cast(list[str], zoneobj.get("flags"))

        no_detailed = "Private" in flags or "Personal" in flags

        if args.resolution_only:
                        no_detailed = True

        for key, value in item.items():
                if key.startswith("lua."):

                        if value[0] == '>':
                                continue

                        rewrite_warning_disabled = itemid.startswith("%verb_")

                        chunkpart = key[4:]

                        error_fn = itemid + "." + key

                        context = dict(default_context)

                        event_validity = check_valid_event(chunkpart)

                        return_type = None

                        if not event_validity:
                                if args.unknown:
                                        error(f"unknown event {chunkpart}")
                        elif isinstance(event_validity, dict):
                                context = event_validity
                        elif isinstance(event_validity, MudEvent):
                                for event_arg, event_value in event_validity.items():
                                        context[event_arg] = event_value
                                return_type = event_validity.return_type

                        if itemid and itemid not in TREATAS_USERS:
                                context["o1"] = TypeSpecificMudObject(item)
                        else:
                                specifics = list(TypeSpecificMudObject(obj) for obj in TREATAS_USERS[itemid])
                                context["o1"] = TypeUnion(*specifics)

                        if key.startswith("lua.lib"):
                                return_type = [TypeAny()]

                        if key.startswith("lua.verb"):
                                return_type = [TypeAny()]

                        context["event"] = TypeMap(context)

                        context = {ckey : cvalue for ckey, cvalue in context.items() if in_global(ckey)}

                        file = itemid + "." + key

                        try:
                                validate_chunk(value, context, rewrite_warning_disabled, itemid, no_detailed = no_detailed, return_type = return_type)
                        except KeyboardInterrupt:
                                print("interrupting")
                                exit(1)
                                raise
                        except:
                                import traceback
                                traceback.print_exc()
                                print("failure in", file)
                                got_error = True
                                raise

#        for file in glob.glob(TMP_PREFIX + "*lua*"):
#                process_file(file)

print("Finished validating")

#from functions import verb_scores
#sorted_verb_scores = sorted(verb_scores.items(), key=lambda a: a[1], reverse=True)
#print(sorted_verb_scores)

if got_error:
        exit(1)
