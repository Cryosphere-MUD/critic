from luaparser import ast, astnodes

from musictypes import TypeAny, TypeMudObject, TypeTable, TypeString

from scopes import Scope, NodeScopes, Resolutions, Variable
from typing import Generator

def index_by_identity(lst, item):
    for i, obj in enumerate(lst):
        if obj is item:
            return i
    raise ValueError("Item not found by identity")

def resolve_symbols(tree, state):
        resolution = Resolutions()

        context = state.context
        parents = state.parents
        globals = state.globals

        global_scope = Scope(node=tree)

        scopes = NodeScopes(parents)

        repeat_scopes = {}

        def find_in_scope(node, name, orignode = None):
                assert isinstance(node, (astnodes.Node, list))
                scope = scopes.get(node)
                if scope and name in scope:
                        return scope[name]

                if repeat := repeat_scopes.get(id(node)):
                        return find_in_scope(repeat, name, orignode)

                node = parents.get(node)
                if node:
                        return find_in_scope(node, name)
                if name in globals:
                        return Variable(name=name, scope=global_scope, the_type=globals.get(name))
                return None

        pending_vars = {}

        def add_repeat_scope(test, block):
                repeat_scopes[id(test)] = block

        def add_var(node, name, the_type=None):
                scope = scopes.get(node)
                var = scope.add_var(name, the_type)
                return var

        def add_pending_var(node, name, on_what):
                nonlocal pending_vars
                scope = scopes.get(node)
                pending = Variable(name=name, scope=scope)
                pending_vars.setdefault(id(on_what), []).append(pending)
                return pending

        def flush_pending(node):
                nonlocal pending_vars
                for pending in pending_vars.get(id(node), []):
                        pending.scope.add(pending.name, pending)
                if id(node) in pending_vars:
                        del pending_vars[id(node)]

        class NEXT_STATEMENT:
                pass

        scopes.open(tree)

        add_var(tree, "_G", TypeAny())
        add_var(tree, "_ENV", TypeAny())
        for predef, type in context.items():
#               print(predef, type)
                add_var(tree, predef, type)

        for node in ast.walk(tree):
                parent = parents.get(node)
                grandparent = parents.get(parent) if parent else None

                flush_pending(node)
                flush_pending(NEXT_STATEMENT)

                match node:
                        case astnodes.Block():
                                scopes.open(node)

                        case astnodes.Name():
                                if isinstance(parent, astnodes.Index):
                                        if parent.idx is node and parent.notation == ast.IndexNotation.DOT:
                                                continue

                                if isinstance(parent, astnodes.Invoke):
                                        if parent.func is node:
                                                continue

                                if isinstance(parent, astnodes.Field):
                                        if id(parent.key) == id(node):
                                                continue

                                if isinstance(parent, astnodes.Method):
                                        if id(parent.name) == id(node):
                                                continue

                                if isinstance(grandparent, astnodes.Forin):
                                        if any(id(target) == id(node) for target in grandparent.targets):
                                                continue

                                if isinstance(parent, astnodes.Fornum):
                                        if id(node) == id(parent.target):
                                                continue

                                if isinstance(grandparent, astnodes.LocalAssign):
                                        if any(id(target) == id(node) for target in grandparent.targets):
                                                continue

                                resolved = find_in_scope(node, node.id)

                                if resolved:
                                        assert isinstance(resolved, Variable)
                                        resolution.add_resolution(node, resolved)
                                        continue

                                # for items in scopes.get_enclosing(node):
                                #         print("  scope")
                                #         for i, value in items.items():
                                #                 print("     ", i, value)

                                state.error(f"""unresolved '{node.id}' at""", node=node if node.first_token else parent)

                        case astnodes.Chunk():
                                pass

                        case astnodes.LocalAssign():
                                assert isinstance(parent, list)
                                this_index = index_by_identity(parent, node)

                                # this needs to handle being the last thing in a block
                                # better?
                                next = parent[this_index+1] if this_index+1 < len(parent) else NEXT_STATEMENT

                                for target in node.targets:
                                        assert isinstance(target, astnodes.Name)
                                        var = add_pending_var(node, target.id, next)
                                        resolution.add_resolution(target, var)

                        case astnodes.Assign():
                                for target in node.targets:
                                        if isinstance(target, astnodes.Name):
                                                resolved = find_in_scope(node, target.id)

                                                if resolved:
                                                        assert isinstance(resolved, Variable)
                                                        resolution.add_resolution(target, resolved)
                                                        continue

                                                state.error(f"""global assign '{target.id}' at""", node=node)
                                                continue

                        case astnodes.Forin():
                                scopes.open(node)
                                for target in node.targets:
                                        var = add_pending_var(node, target.id, node.body)
                                        resolution.add_resolution(target, var)

                        case astnodes.Fornum():
                                scopes.open(node)
                                var = add_pending_var(node, node.target.id, node.body)
                                resolution.add_resolution(node.target, var)

                        case astnodes.Repeat():
                                add_repeat_scope(node.test, node.body)

                        case astnodes.Function():
                                scopes.open(node)
                                for target in node.args:
                                        var = add_var(node, target.id)
                                        resolution.add_resolution(target, var)

                        case astnodes.Method():
                                scopes.open(node)
                                add_var(node, "self")
                                for target in node.args:
                                        add_var(node, target.id)

                        case astnodes.LocalFunction():
                                add_var(node, node.name.id)
                                scopes.open(node)
                                for target in node.args:
                                        var = add_var(node, target.id)
                                        resolution.add_resolution(target, var)

                        case astnodes.AnonymousFunction():
                                scopes.open(node)
                                for target in node.args:
                                        if isinstance(target, astnodes.Varargs):
                                                var = add_var(node, "...")
                                                # bit of a cop out but i'll sort this out later)
                                        else:
                                                var = add_var(node, target.id)
                                        resolution.add_resolution(target, var)

        flush_pending(None)

        return resolution, scopes