from luaparser import ast, astnodes
from luatypes import TypeModule, TypeAny, TypeFunction, TypeNumber, TypeFunctionAny, TypeString, TypeBool, TypeNilString, TypeNil, TypeUnionType, TypeTable, TypeUnion, TypeNumberRange, AnyModule, TypeBase, TypeInvalid, TypeStringKnownPrefix, TypeTranslatedString, TypeMap
from mudtypes import TypeMudObjectOrID, TypeMudObject, TypeSpecificMudObject
import mudtypes
from mudversion import is_musicmud
from typing import NamedTuple, Optional
from scopes import Variable

import functions

FUNCTION_MODULES = [functions]

if is_musicmud():
        import mudfunctions
        FUNCTION_MODULES.append(mudfunctions)


def panic(value):
        print("panic")
        exit(value)

class FunctionScope:
        def __init__(self, node):
                self._node = node
                self._rtypes = []

        def add_return(self, rtypes):
                self._rtypes.append(rtypes)

        def returns(self):
                max_len = max(len(rtype) for rtype in self._rtypes) if self._rtypes else 0
                for type in self._rtypes:
                        for r in range(len(type), max_len):
                                type.append(TypeAny())
                return self._rtypes

        def returns_union(self):
                returns = self.returns()
                out = []
                max_len = max(len(rtype) for rtype in self._rtypes) if self._rtypes else 0
                for idx in range(max_len):
                        l = [r[idx] for r in returns]
                        out.append(TypeUnion(*l))
                return out

class ConditionalNarrowing:

        def __init__(self, variable, exclude = None, only = None):

                assert isinstance(variable, Variable)

                self.variable = variable

                assert isinstance(exclude, (type(None), TypeBase))
                assert isinstance(only, (type(None), TypeBase))

                self.exclude = exclude
                self.only = only

        def __iter__(self):
                yield self.variable
                yield self.exclude
                yield self.only


calldata = {}

def countcall(fn):
        name = fn.name
        if isinstance(name, astnodes.Name):
                name = name.id
        global calldata
        if name not in calldata:
                calldata[name] = 0
        calldata[name] += 1


class NarrowingData:
        def __init__(self, data = None):
                self._data = data or {}

        def __contains__(self, variable):
                assert isinstance(variable, Variable)
                return variable in self._data

        def __getitem__(self, variable):
                assert isinstance(variable, Variable)
                return self._data.get(variable)

        def get(self, variable):
                return self._data.get(variable)
        
        def update(self, other):
                self._data.update(other._data)

        def add_narrowing(self, symbol, the_type):
                assert isinstance(symbol, Variable)
                assert isinstance(the_type, TypeBase)

                self._data[symbol] = the_type

        def merge_with_union(self, other):
                new = {}
                for key, type in self._data.items():
                        if other_type := other.get(key):
                                new[key] = TypeUnion(type, other_type)
                return NarrowingData(new)

        def keys(self):
                yield from self._data.keys()

        def __str__(self):
                s = ""
                for symbol, type in self._data.items():
                        if s:
                                s += ", "                        
                        s += str(symbol)
                        s += " = "
                        s += str(type)
                return f"[Narrow {s}]"


class MusicLUAVisitor(ast.ASTRecursiveVisitor):
        def __init__(self, *, universe, state):
                self.state = state

                self._universe = universe
                self._node_types = {}
                self._narrowings = []
                mudtypes.setValidator(self.check_objectid)
                self._return_frames = []
                self._locked = []
                self._condition_narrowings = {}
                self.resolution = state.resolutions
                self._terminating = set()

                self._remembered_narrowings = {}

                self._visit_stack = []

                self.scopes = state.scopes

                self.deferred_validate = []

                self.doing_deferred = 0

        def check_objectid(self, id):

                if id in self._universe:
                        return self._universe.get(id)

                if id.startswith(prefix := "@auto:"):
                        id = id[len(prefix):]
                        id, obj_code = id.split(":")

                        obj = self._universe.get(id)
                        if obj is None:
                                return None

                        auto_part, auto_cloneno = obj_code.split("/")
                        if int(auto_part) >= obj.get("auto.count", 0):
                                return None

                        if int(auto_cloneno) >= obj.get(f"auto.{auto_part}.count", 1):
                                return None

                        return obj.get(f"auto.{auto_part}")

                if id.startswith("@wild_"):
                        return True

                if id.startswith("@skin_"):
                        return True

                if id == "@pl":
                        return True

        def start_return_scope(self, node):
                self._return_frames.append(FunctionScope(node))

        def end_return_scope(self):
                return self._return_frames.pop()

        def error(self, txt, node = None, level="error"):
                self.state.error(txt, node if node else self.this(), level=level)

        def warning(self, txt, node = None):
                self.error(txt, node, level="warning")

        def do_find_symbol(self, name):
                assert isinstance(name, astnodes.Name)
                return self.state.resolutions.get(name)

        def find_symbol(self, name):
                found_type = self.do_find_symbol(name)
                return found_type

        def ancestors(self, node):
                assert node

                while node:
                        assert isinstance(node, (astnodes.Node, list))
                        yield node
                        node = self.state.parents.get(node)

        def get_narrowed(self, symbol, node, skip_narrowing = []):
                if symbol is not None:

                        for ancestor in self.ancestors(node):
                                if anc := self._previous_assumptions.get(id(ancestor)):
                                        for cond_symbol, exclude, only in self._condition_narrowings.get(id(anc), []):
                                                if cond_symbol == symbol:
                                                        if exclude is not None:
                                                                return symbol.the_type.difference(exclude)
                                                        if only is not None:
                                                                return only

                        for narrow in reversed(self._narrowings):
                                if narrow in skip_narrowing:
                                        continue

                                if symbol in narrow:

                                        the_type = narrow[symbol]
                                        assert isinstance(the_type, (type(None), TypeBase))
                                        return the_type


        def get_type(self, node, allow_none = False, noisy = False, get_tuple = False, skip_narrowing = []):
                assert(isinstance(node, astnodes.Node))

                if isinstance(node, astnodes.Name):
                        symbol = self.find_symbol(node)
                        if narrowed := self.get_narrowed(symbol, node, skip_narrowing):
                                return narrowed
 
                found_type = self._node_types.get(id(node))

                if not get_tuple and isinstance(found_type, tuple):
                        return found_type[0]

                if found_type is None and not allow_none:
                        self.error(f"{type(node)} didn't set a type", node)
                        return TypeInvalid()

                return found_type

        def get_narrowing(self, symbol):
                assert isinstance(symbol, Variable)
                for narrow in reversed(self._narrowings):
                        if symbol in narrow:
                                return narrow[symbol]

                return symbol

        def get_types(self, nodes):
                return [self.get_type(node) for node in nodes]

        def set_type(self, node, the_type):
                assert(isinstance(node, astnodes.Node))
                if isinstance(the_type, Variable):
                        the_type = the_type.the_type
                
                assert(the_type is not None)
                if isinstance(the_type, tuple):
                        for subtype in the_type:
                                assert(isinstance(subtype, TypeBase))
                else:
                        assert(isinstance(the_type, TypeBase))

                self._node_types[id(node)] = the_type

        def set_terminating(self, node, value):
                if value:
                        self._terminating.add(id(node))

        def is_terminating(self, node):
                return id(node) in self._terminating

        def is_negative_test(self, test):
                if isinstance(test, astnodes.OrLoOp):
                        yield from self.is_negative_test(test.left)
                        yield from self.is_negative_test(test.right)

                if isinstance(test, astnodes.ULNotOp):
                        if isinstance(test.operand, astnodes.Name):
                                yield test.operand

                if isinstance(test, astnodes.EqToOp) and (isinstance(test.left, astnodes.Name) and 
                        isinstance(test.right, astnodes.Nil)):
                        yield test.left
                        
        def _impl_visit(self, node):
                if isinstance(node, astnodes.Node):
                        # call enter node method
                        # if no visitor method found for this arg type,
                        # search in parent arg type:
                        parent_type = node.__class__
                        while parent_type != object:
                                name = "enter_" + parent_type.__name__
                                tree_visitor = getattr(self, name, None)
                                if tree_visitor:
                                        tree_visitor(node)
                                        break
                                else:
                                        parent_type = parent_type.__bases__[0]

                        # visit all object public attributes:
                        children = [
                                attr for attr in node.__dict__.keys() if not attr.startswith("_")
                        ]

                        if "body" in children:
                                if not isinstance(node, astnodes.Repeat):
                                        children.remove("body")
                                        children.append("body")
                                else:
                                        children.remove("body")
                                        children.insert(0, "body")

                        for child in children:
                                self.visit(node.__dict__[child])

                        # call exit node method
                        # if no visitor method found for this arg type,
                        # search in parent arg type:
                        parent_type = node.__class__
                        while parent_type != object:
                                name = "exit_" + parent_type.__name__
                                tree_visitor = getattr(self, name, None)
                                if tree_visitor:
                                        tree_visitor(node)
                                        break
                                else:
                                        parent_type = parent_type.__bases__[0]
                elif isinstance(node, list):
                        for n in node:
                                self.visit(n)

        def visit(self, here):
                self._visit_stack.append(here)

                if (isinstance(here, astnodes.Block) and
                    isinstance(self.parent(), (astnodes.Function, astnodes.LocalFunction, astnodes.AnonymousFunction))):
                        parent_type = self.get_type(self.parent(), allow_none = True)

                        if parent_type and parent_type.visiting_from_call:
                                self._impl_visit(here)
                else:
                        self._impl_visit(here)

                self._visit_stack.pop()

        def grandparent(self):
                return self._visit_stack[-3]

        def parent(self):
                return self._visit_stack[-2]

        def this(self):
                return self._visit_stack[-1]

        def visit_stack(self, idx):
                return self._visit_stack[idx]

        def match_stack(self, *args):
                idx = -2
                for arg in args:
                        if not isinstance(self._visit_stack[idx], arg):
                                return False
                        idx -= 1
                return True
        

        def exit_Chunk(self, node):
                for type in self.deferred_validate:
                        if type.deferred_validate:
                                self.doing_deferred += 1
                                self.visit(type.node.body)
                                self.doing_deferred -= 1
                                type.deferred_validate = False

        def enter_Function(self, node):
                self.start_return_scope(node)
                for arg in node.args:
                        if isinstance(arg, astnodes.Name):
                                self.find_symbol(arg).set_type(TypeAny())
                        elif isinstance(arg, astnodes.Varargs):
                                pass
                        else:
                                self.error("unknown function argument type", arg)

        def exit_Function(self, node):
                self.end_return_scope()

        def enter_Method(self, node):
                self.start_return_scope(node)

                self.scopes.get(node).get("self").set_type(TypeAny())

                for arg in node.args:
                        if isinstance(arg, astnodes.Name):
                                self.find_symbol(arg).set_type(TypeAny())
                        elif isinstance(arg, astnodes.Varargs):
                                pass
                        else:
                                self.error("unknown method argument type", arg)

        def exit_Method(self, node):
                self.end_return_scope()

        def mark_deferred_validate(self, node, type):
                self.deferred_validate.append(type)
                type.deferred_validate = True
                type.node = node


        def enter_LocalFunction(self, node):
                self.start_return_scope(node)

                self.find_symbol(node.name).set_type(type := TypeFunctionAny(name=node.name))

                self.mark_deferred_validate(node, type)

                for arg in node.args:
                        if isinstance(arg, astnodes.Name):
                                self.find_symbol(arg).set_type(TypeAny())
                        elif isinstance(arg, astnodes.Varargs):
                                pass
                        else:
                                self.error("unknown arg definition", arg)
                                return

        def exit_LocalFunction(self, node):
                self.end_return_scope()


        def common_condition(self, condition):

                if isinstance(condition, astnodes.Assign):
                        self.warning("assignment used as test", condition)

                test_type = self.get_type(condition.test)
                if isinstance(test_type, TypeNumber) and test_type.get_single_number() is None:
                        self.warning("using number as test (remember that 0 is truthy)", condition)

        # no enter_While
        def exit_While(self,  node):

                self.common_condition(node)


        # no enter_Repeat
        def exit_Repeat(self,  node):

                self.common_condition(node)

        # no enter_If

        def enter_ElseIf(self, node):
                self._narrowings.append(NarrowingData())
                if checkings := self.is_negative_test(self.parent().test):
                        for checking in checkings:
                                symbol = self.find_symbol(checking)
                                the_type = self.get_type(checking)
                                self._narrowings[-1].add_narrowing(symbol, the_type.denil())

        def exit_ElseIf(self, node):
                self._narrowings.pop()

        def exit_If(self,  node):

                self.common_condition(node)

                class ReturnStatus:
                      Terminates = 0
                      MissingElse = 1
                      Regular = 2  

                def navigate_chain(node):
                        if isinstance(node, astnodes.ElseIf):
                                yield from navigate_chain(node.body)
                                yield from navigate_chain(node.orelse)
                                return
                        
                        if isinstance(node, astnodes.If):
                                yield from navigate_chain(node.body)
                                yield from navigate_chain(node.orelse)
                                return

                        if not isinstance(node, astnodes.Block):
                                yield ReturnStatus.MissingElse, None
                                return

                        for code in node.body:
                                if self.is_terminating(code):
                                        yield ReturnStatus.Terminates, None
                                        return

                        remembered = self._remembered_narrowings[id(node)]

                        yield ReturnStatus.Regular, remembered

                possibilities = list(navigate_chain(node))

                if isinstance(node.body, astnodes.Block) and node.orelse is None:
                        if checkings := self.is_negative_test(node.test):
                                for checking in checkings:
                                        symbol = self.find_symbol(checking)
                                        the_type = self.get_type(checking)

                                        if self.is_terminating(node.body):

                                                self._narrowings[-1].add_narrowing(symbol, the_type.denil())

                                        else:
                                                if narrowings := self._remembered_narrowings.get(id(node.body)):
                                                        
                                                        if narr := narrowings.get(symbol):
                                                                
                                                                but_narrowed = the_type.difference(TypeNil()).difference(TypeBool())
                                                                and_expanded = but_narrowed.union(narr)

                                                                self._narrowings[-1].add_narrowing(symbol, and_expanded)

                if all(poss[0] == ReturnStatus.Terminates for poss in possibilities):
                        self.set_terminating(node, True)

                if any(poss[0] == ReturnStatus.MissingElse for poss in possibilities):
                        return
                
                union = None

                for returns, poss in possibilities:
                        if returns == ReturnStatus.Regular:
                               if not union:
                                        union = poss
                               else:
                                        union = union.merge_with_union(poss)

                if union:
                        self._narrowings[-1].update(union)

        # no enter LocalAssign

        def exit_LocalAssign(self, node):

                for target, value in zip(node.targets, node.values):

                        target_var = self.resolution.get(target)

                        if not target_var:
                                self.error("unknown target of assign", target)
                                return

                        if target_var.the_type:
                                self.error("local assign already has type", target)
                                return

                        value_type = self.get_type(value)
                        if value_type is None:
                                self.error(f"not found type of {type(value)}", value)
                                panic(1)

                        target_var.set_type(value_type)
                        target_var.return_frame = self._return_frames[-1] if self._return_frames else None

                for target in node.targets[len(node.values):]:
                        if isinstance(target, astnodes.Name):
                                target_var = self.resolution.get(target)
                                target_var.set_type(TypeAny())
                                target_var.return_frame = self._return_frames[-1] if self._return_frames else None
        # no enter_Assign

        def exit_Assign(self, node):
                if len(node.targets) > 1 and len(node.values) == 1:
                        for target in node.targets:
                                if isinstance(target, astnodes.Name):
                                        symbol = self.find_symbol(target)
                                        if not symbol:
                                                self.error("failing on", target.id)
                                                print(ast.to_pretty_str(node))                                
                                                exit(1)
                                        symbol.set_type(TypeAny())


                for target, value in zip(node.targets, node.values):
                        if isinstance(target, astnodes.Name):
                                symbol = self.find_symbol(target)
                                value_type = self.get_type(value)
                                new_value_type = value_type

                                if value_type is None or symbol is None:
                                        self.error(f"not found type of {type(value)}", value)
                                        return

                                old_type = symbol.the_type
                                value_type = value_type.union(old_type)

                                if isinstance(node, astnodes.LocalAssign):
                                        self.add_to_scope(target.id, value_type)
                                else:

                                        # chunk, block, list, if
                                        if (self.match_stack(list, astnodes.Block, astnodes.If,
                                                             list, astnodes.Block, astnodes.Chunk)
                                            and self.visit_stack(-4).body is self.visit_stack(-3)):
                                                    
                                                    test = self.visit_stack(-4).test
                                                    if (isinstance(test, astnodes.EqToOp) and
                                                        isinstance(test.left, astnodes.Name)):
                                                        
                                                            var = self.find_symbol(test.left)

                                                            if var.the_type == old_type:
                                                                eliminated = self.get_type(test.right)
                                                                value_type = value_type.difference(eliminated)

                                        symbol = self.find_symbol(target)
        
                                        if symbol in self._locked:
                                                if symbol.the_type != value_type:
                                                        self.warning(f"rewriting type of {symbol} from {symbol.the_type} to {value_type} after it was used in a function context")

                                        symbol.set_type(value_type)

                                        self._narrowings[-1].add_narrowing(symbol, new_value_type)

        def enter_AnonymousFunction(self, node):
                self.start_return_scope(node)

                for arg in node.args:
                        if isinstance(arg, astnodes.Name):
                                self.find_symbol(arg).set_type(TypeAny())
                        elif isinstance(arg, astnodes.Varargs):
                                pass
                        else:
                                self.error("bad arg on anon function", arg)
                                return

        def exit_AnonymousFunction(self, node):
                args = [TypeAny() for arg in node.args]

                name = "{anonymous}"

                if isinstance(self.grandparent(), astnodes.Assign):
                        if self.grandparent().values[0] is node:
                                if isinstance(self.grandparent().targets[0], astnodes.Name):
                                        name = "local " + self.grandparent().targets[0].id

                type = TypeFunction(name=name, args=args, min_args=0)
                self.mark_deferred_validate(node, type)

                self.set_type(node, type)
                self.end_return_scope()

        def enter_Block(self, node):
                self._narrowings.append(NarrowingData())

                parent = self.parent()

                if isinstance(self.parent(), astnodes.Forin):
                        assert len(self.parent().iter) == 1
                        iter = self.parent().iter[0]
                        iter_type = self.get_type(iter, get_tuple=True)

                        if isinstance(iter_type, TypeAny):
                                for target in self.parent().targets:
                                        self.find_symbol(target).set_type(iter_type)
                                return

                        for target, it_type in zip(self.parent().targets, iter_type):
                                self.find_symbol(target).set_type(it_type)
                                cond_symbol = self.find_symbol(target)
                                self._narrowings[-1].add_narrowing(cond_symbol, it_type)

                if isinstance(self.parent(), astnodes.Fornum):
                        parent = self.parent()

                        start_type = self.get_type(parent.start, allow_none=True)
                        end_type = self.get_type(parent.stop, allow_none=True)

                        loop_var = self.find_symbol(parent.target)

                        number_type = TypeNumber()

                        if isinstance(start_type, TypeNumberRange) and isinstance(end_type, TypeNumberRange):
                                number_type = TypeNumberRange(start_type.min_value, end_type.max_value)

                        loop_var.set_type(number_type)

                if isinstance(self.parent(), (astnodes.If, astnodes.ElseIf)) and id(self.parent().body) == id(node):
                        the_if = self.parent()

                        conds = self._condition_narrowings.get(id(the_if.test))
                        if conds is not None:
                                for symbol, exclusion, only in conds:
                                        current_type = self.get_narrowed(symbol, node)
                                        if not current_type:
                                                current_type = symbol.the_type
                                                
                                        if exclusion:
                                                self._narrowings[-1].add_narrowing(symbol, current_type.difference(exclusion))
                                        if only:
                                                self._narrowings[-1].add_narrowing(symbol, only)

                if isinstance(self.parent(), (astnodes.If, astnodes.ElseIf)) and id(self.parent().orelse) == id(node):

                        if checkings := self.is_negative_test(self.parent().test):
                                for checking in checkings:
                                        symbol = self.find_symbol(checking)
                                        the_type = self.get_type(checking)
                                        self._narrowings[-1].add_narrowing(symbol, the_type.denil())

        def exit_Block(self, node):
                for child in node.body:
                        if self.is_terminating(child):
                                self.set_terminating(node, True)

                self._remembered_narrowings[id(node)] = self._narrowings[-1]
                self._narrowings.pop()

        def handle_function_call(self, node, func: TypeFunction, args):
                countcall(func)
                args_valid = self.validate_args(func, args)
                rtype = self.get_binding_return_type(func, args, args_valid)
                self.set_type(node, rtype)
                self.set_terminating(node, func.no_return)

        # no enter_Invoke

        def exit_Invoke(self, node):
                source = node.source

                source_type = self.get_type(source)

                if isinstance(source_type, TypeAny):
                        #self.warning(f"method {node.func.id} called on any")
                        self.set_type(node, TypeAny())
                        return

                if isinstance(source_type, (AnyModule, TypeTable)):
                        self.set_type(node, TypeAny())
                        return

                args = [node.source] + node.args

                if isinstance(source_type, TypeMudObject):
                        class_methods = self.state.class_methods

                        if node.func.id not in class_methods["mudobject"]:
                                self.error(f"method {node.func.id} not found on mudobject", node.func)
                                return

                        func = class_methods["mudobject"][node.func.id]
                        self.handle_function_call(node, func, args)
                        return
                
                if isinstance(source_type, TypeString):
                        if node.func.id in ("sub", "gsub"):
                                self.set_type(node, TypeAny())
                                return

                if isinstance(source_type, TypeUnionType):
                        for specific in source_type.types():
                                if isinstance(specific, (TypeMudObject, TypeSpecificMudObject)):
                                        if node.func.id not in self.state.class_methods["mudobject"]:
                                                self.error(f"method {node.func.id} not found on mudobject", node.func)
                                                return

                                        continue

                                self.error(f"invoke on unhandled option {specific} state.n {source_type}", node.source)
                                return

                        func = self.state.class_methods["mudobject"][node.func.id]
                        self.handle_function_call(node, func, args)
                        return

                self.error(f"invoke on unhandled source {source_type}", node)
                self.set_type(node, TypeAny())

        # no enter_Name

        def exit_Name(self, node):
                symbol = self.do_exit_Name(node)
                if symbol:
                        self.set_type(node, symbol)

        def do_exit_Name(self, node):
                parent = self.parent()

                if (isinstance(parent, astnodes.Index) and
                        node is parent.idx and parent.notation == ast.IndexNotation.DOT):
                        # we're after the . in blah.foo
                        return

                if (isinstance(parent, astnodes.Invoke) and
                    parent.func is node):
                        # we're the blah after the : in o1:blah(), Invoke will look us up (when I add this)
                        return

                if (isinstance(parent, astnodes.Field) and 
                     parent.key is node):
                        # we're the field in a dict initializer
                        return  

                if (isinstance(self.grandparent(), astnodes.LocalAssign) and
                    id(node) in (id(target) for target in self.grandparent().targets)):
                        return # we have to do this id() nonsense as in local a = a the as will ==

                if (isinstance(self.grandparent(), astnodes.Assign) and
                    id(node) in (id(target) for target in self.grandparent().targets)):
                        return # we have to do this id() nonsense as in local a = a the as will ==

                if (isinstance(parent, astnodes.Method) and
                    node in (parent.source, parent.name)):
                        # we're the the thing or blah in function thing:blah
                        return

                if (isinstance(parent, list) and
                   isinstance(self.grandparent(), astnodes.Forin) and
                   node in self.grandparent().targets):
                        # we resolve these types when entering the body
                        return

                if (isinstance(parent, astnodes.Fornum) and
                    node is parent.target):
                        # we're the loop variable in a fornum
                        return

                name = node.id

                symbol = self.find_symbol(node)

                if not symbol:
                        self.error(f"unresolved name '{name}' used", node)
                        return

                if not symbol.the_type:
                        self.error(f"symbol '{symbol}' used without established type", node)
                        panic(1)

                if (self._return_frames and symbol.return_frame and 
                    symbol.return_frame is not self._return_frames[-1]):

                        if (isinstance(self.grandparent(), astnodes.Assign) and
                                id(node) in (id(target) for target in self.grandparent().targets)):

                                # don't lock if all the subfunction is doing is an assign

                                pass
                        else:
                                self._locked.append(symbol)

                self._condition_narrowings[id(node)] = [ConditionalNarrowing(symbol, exclude=TypeNil())]

                return symbol

        def enter_Nil(self, node):
                self.set_type(node, TypeNil())

        # no exit_Nil
        
        def enter_Number(self, node):
                self.set_type(node, TypeNumberRange(node.n))

        # no exit_Number

        def enter_String(self, node):
                self.set_type(node, TypeString(node.s, tainted=False))

        # no exit_String

        def exit_Dots(self, node):
                self.set_type(node, TypeAny())

        # no enter_Table

        def exit_Table(self, node):
                table = {}
                non_numeric = False

                for f in node.fields:
                        
                        if isinstance(f.key, astnodes.Name):
                                string = True
                                key = f.key.id
                        elif isinstance(f.key, astnodes.Number):
                                key = f.key.n
                        elif isinstance (f.key, astnodes.String):
                                string = True
                                key = f.key.s
                        else:
                                self.error(f"unexpected key {f.key} in table", f.key)
                                panic(1)

                        if isinstance(key, str):
                                non_numeric = True

                        table[key] = self.get_type(f.value)

                self.set_type(node, TypeTable(table, non_numeric=non_numeric))

        def exit_ULNotOp(self, node):
                self.set_type(node, TypeBool())
                operand_type = self.get_type(node.operand, allow_none=True)
                if id(node.operand) in self._condition_narrowings:
                        op_conds = self._condition_narrowings.get(id(node.operand))
                        # i think this doesn't extend to more than one because of
                        # DeMorgan's theoreom but I need to check
                        if len(op_conds) != 1:
                                return

                        symbol, exclude, only = op_conds[0]

                        # self._condition_narrowings_for_else[id(node)] = [ConditionalNarrowing(symbol, exclude=only, only=exclude)]

        def exit_EqToOp(self, node):
                self.set_type(node, TypeBool())

                if isinstance(node.left, astnodes.Name):
                        left_symbol = self.find_symbol(node.left)
                        right_type = self.get_type(node.right, allow_none=True)

                        if right_type is None:
                                return
                
                        self._condition_narrowings[id(node)] = [ConditionalNarrowing(left_symbol, only=right_type)]

        def exit_NotEqToOp(self, node):
                self.set_type(node, TypeBool())

                if isinstance(node.left, astnodes.Name):
                        left_symbol = self.find_symbol(node.left)
                        right_type = self.get_type(node.right, allow_none=True)

                        if right_type is None:
                                return

                        self._condition_narrowings[id(node)] = [ConditionalNarrowing(left_symbol, exclude=right_type)]

        def exit_AndLoOp(self, node):
                hereconds = []
                for part in [node.left, node.right]:
                        if id(part) in self._condition_narrowings:
                                hereconds.extend(self._condition_narrowings.get(id(part)))

                self._condition_narrowings[id(node)] = hereconds

                self._narrowings.pop()
                self.set_type(node, TypeAny())
        
        _previous_assumptions = {}

        def enter_AndLoOp(self, node):

                self._previous_assumptions[id(node.right)] = node.left

                self._narrowings.append(NarrowingData())

        def exit_ULengthOP(self, node):
                op_type = self.get_type(node.operand)
                if isinstance(op_type, TypeTable):
                        if items := op_type.items():
                                self.set_type(node, TypeNumberRange(len(items)))
                                return
                self.set_type(node, TypeAny())

        def exit_TrueExpr(self, node):
                self.set_type(node, TypeBool(True))

        def exit_FalseExpr(self, node):
                self.set_type(node, TypeBool(False))

        def exit_GreaterThanOp(self, node):
                self.set_type(node, TypeBool())

        def exit_GreaterOrEqThanOp(self, node):
                self.set_type(node, TypeBool())

        def exit_LessOrEqThanOp(self, node):
                self.set_type(node, TypeBool())

        def exit_LessThanOp(self, node):
                self.set_type(node, TypeBool())

        def exit_FloatDivOp(self, node):
                self.set_type(node, TypeNumber())

        def exit_ModOp(self, node):
                self.set_type(node, TypeNumber())

        def exit_MultOp(self, node):
                self.set_type(node, TypeNumber())

        def exit_ExpoOp(self, node):
                self.set_type(node, TypeNumber())

        def exit_EqToOp(self, node):
                self.set_type(node, TypeBool())

        def exit_BOrOp(self, node):
                self.set_type(node, TypeAny())

        def exit_BAndOp(self, node):
                self.set_type(node, TypeAny())

        def exit_OrLoOp(self, node):
                left_type = self.get_type(node.left)
                right_type = self.get_type(node.left)

                self.set_type(node, TypeUnion(left_type, right_type))

        def exit_UMinusOp(self, node):

                # if isinstance(left_type, TypeAny) or isinstance(right_type, TypeAny):
                #         return

                the_type = self.get_type(node.operand)

                if isinstance(the_type, TypeNumber):
                        single = the_type.get_single_number()
                        if single is not None:
                                self.set_type(node, TypeNumber(-single))
                                return

                        if isinstance(the_type, TypeNumberRange):
                                self.set_type(node, TypeNumber(-the_type.max_value, -the_type.min_value))
                                return

                self.set_type(node, TypeNumber())

        def exit_SubOp(self, node):
                left_type = self.get_type(node.left)
                right_type = self.get_type(node.right)

                # if not TypeNumber().convertible_from(left_type):
                #         self.error(f"not convertible to number", node.left)
                # if not TypeNumber().convertible_from(right_type):
                #         self.error(f"not convertible to number", node.right)

                lhs_num = left_type.get_single_number()
                rhs_num = right_type.get_single_number()

                if lhs_num is None or rhs_num is None:
                        self.set_type(node, TypeNumber())
                        return

                self.set_type(node, TypeNumberRange(lhs_num - rhs_num))

        def exit_AddOp(self, node):
                left_type = self.get_type(node.left)
                right_type = self.get_type(node.right)

                lhs_num = self.get_type(node.left)
                rhs_num = self.get_type(node.right)

                if not TypeNumber().coercible_from(left_type):
                        self.error(f"{left_type} not convertible to number", node.left)
                if not TypeNumber().coercible_from(right_type):
                        self.error(f"{right_type} not convertible to number", node.right)

                if (isinstance(left_type, TypeNumberRange) and isinstance(right_type, TypeNumberRange)):
                        self.set_type(node, TypeNumberRange(left_type.min_value + right_type.min_value,
                                                      left_type.max_value + right_type.max_value))
                else:
                        self.set_type(node, TypeNumber())

        def exit_Concat(self, node):
                left_type = self.get_type(node.left)
                right_type = self.get_type(node.right)

                if not TypeString().convertible_from(left_type):
                        self.error(f"lhs to concat of type {left_type} is not convertible to string", node.left)
                if not TypeString().convertible_from(right_type):
                        self.error(f"rhs to concat of type {right_type} is not convertible to string", node.right)

                if isinstance(left_type, TypeTranslatedString):
                        self.warning("suspicious concat of translated string", node.left)

                if isinstance(right_type, TypeTranslatedString):
                        self.warning("suspicious concat of translated string", node.right)

                if isinstance(left_type, TypeString) and len(left_type.values)==1:
                        if isinstance(right_type, TypeString):
                                if len(right_type.values) == 1:
                                        res = TypeString(left_type.values[0] + right_type.values[0], tainted=
                                                         left_type.tainted or right_type.tainted)
                                        self.set_type(node, res)
                                        return

                        if isinstance(right_type, TypeNumberRange):
                                candidates = []
                                for value in range(right_type.min_value, right_type.max_value+1):
                                        candidates.append(left_type.values[0] + str(value))
                                self.set_type(node, TypeString(*candidates, tainted=left_type.tainted))
                                return

                        tainted = left_type.tainted

                        if isinstance(right_type, TypeString):
                                tainted |= right_type.tainted

                        self.set_type(node, TypeStringKnownPrefix(left_type.values[0], tainted=tainted))
                        return
                
                if isinstance(left_type, TypeString) and isinstance(right_type, TypeString):
                        self.set_type(node, TypeString(tainted=False))
                        return

                if isinstance(left_type, TypeNumber) and isinstance(right_type, TypeString):
                        self.set_type(node, TypeString(tainted=right_type.tainted))
                        return
                
                if isinstance(right_type, TypeNumber) and isinstance(left_type, TypeString):
                        self.set_type(node, TypeString(tainted=left_type.tainted))
                        return

                self.set_type(node, TypeString())

        def exit_Index(self, node):

                symbol_type = self.get_type(node.value)
        
                # this handles the o1.rooms.count case
                if (not isinstance(symbol_type, TypeAny) and
                    node.notation == ast.IndexNotation.DOT and 
                    isinstance(node.value, astnodes.Index) and 
                    node.value.notation == ast.IndexNotation.DOT):

                        str_value = None

                        if isinstance(node.value.value, astnodes.Name):
                                inner_symbol_type = self.get_type(node.value.value)
                                if isinstance(inner_symbol_type, TypeMudObject):
                                        str_value = node.value.idx.id + "." + node.idx.id
                
                        self.set_type(node, TypeAny())

                        if str_value:
                                if field_type := inner_symbol_type.check_field(str_value):
                                        self.set_type(node, field_type)
                                else:
                                        # self.warning(f"unknown field {str_value} on {symbol_type.id}")
                                        # these actually come out as Nil if they're not defined
                                        self.set_type(node, TypeAny())

                        return

                if isinstance(node.value, astnodes.Name):
                        symbol = self.find_symbol(node.value)

                        if symbol is None:
                                self.error(f"unrecognised table {node.value}", node.value)
                                return

                        if isinstance(symbol_type, TypeAny):
                                if isinstance(node.idx, astnodes.Name) and node.idx.id == "id":
                                        self.set_type(node, TypeString(tainted=False))
                                        return

                                self.set_type(node, TypeAny())
                                return

                        if isinstance(symbol_type, AnyModule):
                                self.set_type(node, TypeFunctionAny(name="*"))
                                return

                        if isinstance(symbol_type, TypeModule):

                                if node.notation == ast.IndexNotation.DOT:
                                        if not symbol_type.contains(node.idx.id):
                                                self.error(f"unrecognised {symbol.name}.{node.idx.id}", node)
                                                exit(1)
                                        self.set_type(node, symbol.the_type.lookup(node.idx.id) or TypeInvalid())
                                        return

                                if node.notation == ast.IndexNotation.SQUARE:
                                        if isinstance(node.idx, astnodes.String):
                                                if not symbol_type.contains(node.idx.s):
                                                        self.error(f"unrecognised {symbol.name}.{node.s.id}")
                                                        exit(1)
                                                self.set_type(node, symbol_type.lookup(node.idx.s))
                                                return

                                        if isinstance(node.idx, (astnodes.Name, astnodes.Index)):
                                                # we will need to remember what values that can have
                                                self.set_type(node, TypeAny())
                                                return

                if isinstance(symbol_type, (TypeSpecificMudObject, TypeMudObject)):
                        str_value = None
                        if isinstance(node.idx, ast.String):
                                str_value = node.idx.s
                        if isinstance(node.idx, ast.Name):
                                str_value = node.idx.id

                        if symbol_type.is_invoker and str_value == "id":
                                self.set_type(node, TypeString("@pl", tainted=False))
                                return

                        self.set_type(node, TypeAny())

                        if str_value:
                                if field_type := symbol_type.check_field(str_value):
                                        self.set_type(node, field_type)
                                else:
                                        # self.warning(f"unknown field {str_value} on {symbol_type.id}")
                                        # these actually come out as Nil if they're not defined
                                        self.set_type(node, TypeAny())

                        return

                if isinstance(symbol_type, TypeUnionType):
                        for specific in symbol_type.types():
                                if isinstance(specific, (TypeSpecificMudObject, TypeMudObject, TypeTable)):
                                        continue

                                self.error(f"unhandled type option {specific} in {node.value.id}")
                                self.set_type(node, TypeAny())
                                return

                        self.set_type(node, TypeAny())
                        return
                
                if isinstance(symbol_type, TypeTable):

                        if node.notation == ast.IndexNotation.SQUARE:

                                nar = self.get_type(node.idx)

                                if isinstance(nar, TypeAny):
                                        self.set_type(node, TypeAny())
                                        return

                                types = set()
                        
                                if symbol_type._table and isinstance(nar, TypeNumberRange):
                                        for v in range(nar.min_value, nar.max_value + 1):
                                                if v in symbol_type._table:
                                                        types.add(symbol_type._table.get(v))
                                                else:
                                                        # self.warning(f"{v} doesn't exist in {symbol_type}", node)
                                                        types.add(TypeAny())
                                else:
                                        if symbol_type.value is not None:
                                                types.add(symbol_type.value)
                                        else:
                                                types.add(TypeAny())

                                resulting = TypeUnion(*types)
                                self.set_type(node, resulting)
                                return
                        
                        self.set_type(node, TypeAny())
                        return

                if isinstance(symbol_type, TypeMap):
                        if node.notation == ast.IndexNotation.DOT:
                                assert isinstance(node.idx, astnodes.Name)
                                the_type = symbol_type.get_member(node.idx.id)
                                if the_type is None:
                                        self.error(f"no field {node.idx.id} in {symbol}", node.idx)
                                self.set_type(node, the_type)
                                return
                        self.set_type(node, TypeAny())
                        return 

                if isinstance(symbol_type, TypeNil):
                        self.error("index on nil object", node)
                        return

                # to do these we will need actual type inference
                if isinstance(node.value, (astnodes.Call, astnodes.Invoke, astnodes.Index)):
                        self.set_type(node, TypeAny())
                        return

#                self.dump_scopes()

                self.error(f"index on unrecognised thing {node.value.id} {node.value} with type {symbol_type}", node)
                panic(1)

        def lookup_mudobject(self, arg):
                if isinstance(arg, TypeString) and arg.values:
                        if self._universe.get(arg.values[0]):
                                obj = self._universe.get(arg.values[0])
                                if obj:
                                        return TypeSpecificMudObject(obj)
                return TypeMudObject()

        def validate_args(self, function, args):
                assert function is not None

                if isinstance(function, TypeAny):
                        return True

                wanted_args = [function.get_argtype(i) if i < function.max_args else TypeAny() for i in range(len(args))]
                real = [self.get_type(arg) for arg in args]

                if function.is_global or function.module:
                        if function.module:
                                fn_name = "global_" + function.module + "_" + function.name + "_wanted_args"
                        else:
                                fn_name = "global_" + function.name + "_wanted_args"

                        for module in FUNCTION_MODULES:
                                if hasattr(module, fn_name):
                                        fn_impl = getattr(module, fn_name)
                                        if fn_impl:
                                                fn_impl(self, wanted_args, real)
                                        
                if not function.validate_argcount(len(args)):
                        self.error(f"{function.name} called with {len(args)} arguments")
                        return False
                
                for i, (wanted_type, arg_type, arg) in enumerate(zip(wanted_args, real, args)):
                        if i >= function.min_args and isinstance(arg_type, TypeNil):
                                continue

                        if wanted_type.convertible_from(arg_type):
                                continue

                        arg_type = arg_type.denil()

                        if wanted_type.convertible_from(arg_type):
                                arg_text = arg.first_token.text
                                self.warning(f"assuming non-nil {arg_text} in argument {i} call to {function.name}", arg)
                                continue
                        
                        for subtype in arg_type.types():
                                if not wanted_type.convertible_from(subtype):
                                        self.error(f"can't convert {subtype} to {wanted_type} in argument {i} in call to {function.name}", node=arg)
                                        continue

                        if isinstance(arg_type, TypeString) and isinstance(wanted_type.denil(), TypeMudObjectOrID):
                                continue

                        if isinstance(arg_type, TypeMudObject) and isinstance(wanted_type.denil(), TypeMudObjectOrID):
                                continue

                return True

        def get_binding_return_type(self, symbol, args, args_valid):
                from errors import quiet
                if symbol.global_assert:
                        if symbol.name == "print":
                                arg_type = self.get_type(args[0])
                                if isinstance(args[0], astnodes.Name):
                                        arg = self.find_symbol(args[0])
                                        if not quiet:
                                                print(f"print() called on {arg} [{arg.the_type}] narrowed to", {arg_type})
                                elif not quiet:
                                        print(f"print() called on {arg_type}")
                                return symbol.return_type

                        if isinstance(args[0], astnodes.Name):
                                target = args[0]
                                assert_target = self.find_symbol(target)
                                current_type = self.get_type(target)
                                self._narrowings[-1].add_narrowing(assert_target, current_type.denil())

                if args_valid and (symbol.is_global or symbol.module):
                        if symbol.module:
                                fn_name = "global_" + symbol.module + "_" + symbol.name
                        else:
                                fn_name = "global_" + symbol.name

                        for module in FUNCTION_MODULES:
                                if hasattr(module, fn_name):
                                        fn_impl = getattr(module, fn_name)
                                        if fn_impl:
                                                rtype = fn_impl(self, args)
                                                if rtype is None:
                                                        return TypeAny()
                                                return rtype
                
                return symbol.return_type

        def exit_Call(self, node):

                symbol = self.get_type(node.func)

                if symbol.deferred_validate:
                        symbol.visiting_from_call += 1
                        symbol.deferred_validate = False # avoid recursion
                        self.deferred_validate.remove(symbol)
                        self.doing_deferred += 1
                        self.start_return_scope(symbol.node)
                        self.visit(symbol.node.body)
                        returns = self.end_return_scope()
                        self.doing_deferred -= 1
                        return_type = returns.returns_union()
                        self.set_type(node, return_type[0] if return_type else TypeNil())
                        symbol.visiting_from_call -= 1
                        return

                if symbol is not None:

                        if isinstance(symbol, TypeFunction):
                                self.set_type(node, TypeAny())

                                self.handle_function_call(node, symbol, node.args)

                                return
                        
                        if isinstance(symbol, TypeAny):
                                self.set_type(node, TypeAny())
                                return

                self.error(f"call on non-function {symbol}")
                panic(1)

        def exit_Return(self, node):

                self.set_terminating(node, True)

                types = self.get_types(node.values)

                if len(self._return_frames):
                        self._return_frames[-1].add_return(types)
                elif not self.doing_deferred:

                        if not types:
                                return
                        
                        if self.state.expected_return_type == [TypeNil()]:
                                #self.warning(f"unexpected return value in trap with no return expected", node.values[0])
                                return

                        num_expected = len(self.state.expected_return_type or [])

                        for actual, expected, value in zip(types, self.state.expected_return_type or [], node.values):
                                if actual != TypeNil() and not expected.convertible_from(actual.denil()):
                                        self.error(f"return type {actual} not compatible with {expected}", value)

                        if len(types) > num_expected:
                                self.error("unexpected return value", node.values[num_expected])

