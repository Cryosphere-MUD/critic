from luaparser import ast, astnodes

from musictypes import TypeBase

class Scope:

        def __init__(self, node):
                self._values = {}
                self.node = node

        def __iter__(self):
                yield from self._values

        def __getitem__(self, idx):
                return self._values.__getitem__(idx)

        def __contains__(self, value):
                return value in self._values

        def items(self):
                return self._values.items()

        def get(self, idx):
                return self._values.get(idx)

        def get_type(self, idx):
                if symbol := self._values.get(idx):
                        return symbol.the_type
                return None

        def add_var(self, name, the_type=None):
                var = Variable(name, scope=self, the_type=the_type)
                self._values[name] = var                
                return var

        def add(self, name, var):
                self._values[name] = var

class NodeScopes:
        scopes = {}

        def __init__(self, parents):
                self.parents = parents

        def open(self, node):
                assert isinstance(node, astnodes.Node)
                self.scopes[id(node)] = Scope(node)

        def get(self, node):
                assert isinstance(node, (astnodes.Node, list))
                scope = self.scopes.get(id(node))
                if scope is not None:
                        return scope
                node = self.parents.get(node)
                if node:
                        return self.get(node)
                return None

        def get_enclosing(self, node):
                assert isinstance(node, (astnodes.Node, list))
                scope = self.scopes.get(id(node))
                if scope is not None:
                        yield scope
                node = self.parents.get(node)
                if node:
                        yield from self.get_enclosing(node)



class Resolutions:
        resolutions = {}

        def add_resolution(self, node, variable):
                assert isinstance(node, astnodes.Node)
                self.resolutions[id(node)] = variable

        def get(self, node):
                assert isinstance(node, astnodes.Node)
                return self.resolutions.get(id(node))


uniq = 0

class Variable:
        
        def __init__(self, name, scope, the_type=None):
                self.name = name
                self.scope = scope
                self.return_frame = None
                assert the_type is None or isinstance(the_type, TypeBase)
                self.the_type = the_type
                global uniq
                self.count = uniq
                uniq += 1

        def __eq__(self, other):
                return self.name == self.name

        def __hash__(self):
                return hash((type(self), self.name, id(self.scope)))

        def __str__(self):
                return f"[{self.name}#{self.count}]"


        def set_type(self, the_type):
                assert isinstance(the_type, TypeBase)
                self.the_type = the_type