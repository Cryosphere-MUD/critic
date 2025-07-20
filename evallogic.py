from luatypes import TypeNil, TypeUnion, TypeUnionType, TypeBool, TypeAny

class LogicEvaluator:

        def exit_AndLoOp(self, node):
                hereconds = []
                for part in [node.left, node.right]:
                        if id(part) in self._condition_narrowings:
                                hereconds.extend(self._condition_narrowings.get(id(part)))

                self._condition_narrowings[id(node)] = hereconds

                self._narrowings.pop()
                self.set_type(node, TypeAny())
        
        def enter_AndLoOp(self, node):
                
                from visitor import NarrowingData

                self._previous_assumptions[id(node.right)] = node.left

                self._narrowings.append(NarrowingData())

        def exit_OrLoOp(self, node):
                left_type = self.get_type(node.left)
                right_type = self.get_type(node.right)

                types = []
                
                def add_type(type):
                        if type != TypeNil() and type != TypeBool(False):
                                types.append(type)

                if isinstance(left_type, TypeUnionType):
                        for type in left_type.types():
                                add_type(type)

                types.append(right_type)

                self.set_type(node, TypeUnion(*types))

        def exit_ULNotOp(self, node):
                self.set_type(node, TypeBool())
        
                operand_type = self.get_type(node.operand, allow_none=True)
                
                if operand_type == TypeBool(True):
                        self.set_type(node, TypeBool(False))
                elif operand_type == TypeBool(False):
                        self.set_type(node, TypeBool(True))

                if id(node.operand) in self._condition_narrowings:
                        op_conds = self._condition_narrowings.get(id(node.operand))
                        # i think this doesn't extend to more than one because of
                        # DeMorgan's theoreom but I need to check
                        if len(op_conds) != 1:
                                return

                        symbol, exclude, only = op_conds[0]

                        # self._condition_narrowings_for_else[id(node)] = [ConditionalNarrowing(symbol, exclude=only, only=exclude)]

