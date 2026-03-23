import sys, os
from luaparser import ast
from types import MappingProxyType

from mudversion import is_musicmud
from mudtypes import TypeMudObject
from bindings import BINDINGS, MODULE_SYMBOLS, CLASS_METHODS
from bindingsparser import global_symbols
from context import get_default_context
from globals import make_global_scope
from errors import error, got_error
import parents
from symbolresolver import resolve_symbols
from validatorstate import ValidatorState
from visitor import MusicLUAVisitor
from extrachunk import extra_chunks

if is_musicmud():
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/..")
        from lib import universe
        all_context = universe.UNIVERSE_BY_ID
else:
        all_context = None

GLOBALS = None

def validate_chunk(lua, context = None, rewrite_warning_disabled = False, itemid = None, no_detailed = False, return_type = None, const = False):

        if context is None:
                context = get_default_context()

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

        global GLOBALS
        global_scope = make_global_scope(bindings_global)
        GLOBALS = global_scope

        state = ValidatorState()
        state.parents = parents.get_parents(tree)
        state.context = context
        state.const = const
        state.globals = MappingProxyType(global_scope)
        state.source = lua
        state.error_handler = error
        state.class_methods = CLASS_METHODS
        state.object_id = itemid
        state.expected_return_type = return_type

        state.resolutions, state.scopes = resolve_symbols(tree, state)

        if not no_detailed:

                v = MusicLUAVisitor(universe=all_context, state=state)
        
                v.visit(tree)

        extra_added = list(extra_chunks)
        extra_chunks.clear()

        for extra in extra_added:
                validate_chunk(lua=extra.lua, context=dict(pl=TypeMudObject(), o1=TypeMudObject()))
