from luaparser import ast
from types import MappingProxyType

from bindings import BINDINGS, MODULE_SYMBOLS, CLASS_METHODS
from context import default_context
from globals import make_global_scope
from errors import error
import parents
from universe import UNIVERSE_BY_ID
from symbolresolver import resolve_symbols
from validatorstate import ValidatorState
from visitor import MusicLUAVisitor

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
