from luaparser import ast, astnodes

class Parents(ast.ASTRecursiveVisitor):
        def __init__(self):
                self._visit_stack = []
                self.parents = {}
                self._root = None

        def get(self, of):
                assert isinstance(of, (astnodes.Node, list))
                if of == self._root:
                        return None
                return self.parents[id(of)]

        def visit(self, here):
                if self._visit_stack:
                        self.parents[id(here)] = self._visit_stack[-1]
                else:
                        self._root = here
                self._visit_stack.append(here)
                super().visit(here)
                self._visit_stack.pop()

def get_parents(tree):
        parents = Parents()
        parents.visit(tree)
        return parents