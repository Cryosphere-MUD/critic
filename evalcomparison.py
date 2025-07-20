from luaparser import astnodes
from luatypes import TypeBool, TypeNumber, TypeString, TypeAny


def is_comparable(type):
        if type.is_only(TypeNumber):
                return True;
        return isinstance(type, (TypeNumber, TypeString, TypeAny))
        

class ComparisonEvaluator:

        def impl_exit_comparisonOp(self, node, function):
                left_type = self.get_type(node.left)
                right_type = self.get_type(node.right)

                if not is_comparable(left_type):
                        self.error(f"{left_type} not convertible to number or string", node.left)
                if not is_comparable(right_type):
                        self.error(f"{right_type} not convertible to number or string", node.right)

                self.set_type(node, TypeBool())

                if isinstance(left_type, TypeNumber):
                        if isinstance(right_type, TypeString):
                                self.error("comparing number to string!", right_type)
                                return

                        lhs_num = left_type.get_single_number()
                        rhs_num = right_type.get_single_number()

                        if lhs_num is None or rhs_num is None:
                                return
                
                        self.set_type(node, TypeBool(function(lhs_num, rhs_num)))

                if isinstance(left_type, TypeString):
                        if isinstance(right_type, TypeNumber):
                                self.error("comparing number to string!", right_type)
                                return
                
                        lhs_val = left_type.get_single_string()
                        rhs_val = right_type.get_single_string()

                        if lhs_val is None or rhs_val is None:
                                return
                
                        self.set_type(node, TypeBool(function(lhs_val, rhs_val)))



        def exit_EqToOp(self, node):
                from visitor import ConditionalNarrowing

                self.set_type(node, TypeBool())

                left_type = self.get_type(node.left, allow_none=True)
                right_type = self.get_type(node.right, allow_none=True)

                left_single = left_type.get_single_number()
                right_single = right_type.get_single_number()
                if left_single is not None and right_single is not None:
                        self.set_type(node, TypeBool(left_single == right_single))

                if isinstance(node.left, astnodes.Name):
                        left_symbol = self.find_symbol(node.left)

                        if right_type is None:
                                return
                
                        self._condition_narrowings[id(node)] = [ConditionalNarrowing(left_symbol, only=right_type)]

        def exit_NotEqToOp(self, node):
                from visitor import ConditionalNarrowing

                self.set_type(node, TypeBool())

                left_type = self.get_type(node.left, allow_none=True)
                right_type = self.get_type(node.right, allow_none=True)

                left_single = left_type.get_single_number()
                right_single = right_type.get_single_number()
                if left_single is not None and right_single is not None:
                        self.set_type(node, TypeBool(left_single != right_single))

                if isinstance(node.left, astnodes.Name):
                        left_symbol = self.find_symbol(node.left)
                        right_type = self.get_type(node.right, allow_none=True)

                        if right_type is None:
                                return

                        self._condition_narrowings[id(node)] = [ConditionalNarrowing(left_symbol, exclude=right_type)]

        def exit_GreaterThanOp(self, node):
                self.set_type(node, TypeBool())

                self.impl_exit_comparisonOp(node, lambda a, b: a > b)


        def exit_GreaterOrEqThanOp(self, node):
                self.set_type(node, TypeBool())

                self.impl_exit_comparisonOp(node, lambda a, b: a >= b)

        def exit_LessOrEqThanOp(self, node):
                self.set_type(node, TypeBool())

                self.impl_exit_comparisonOp(node, lambda a, b: a <= b)

        def exit_LessThanOp(self, node):
                self.set_type(node, TypeBool())

                self.impl_exit_comparisonOp(node, lambda a, b: a < b)

