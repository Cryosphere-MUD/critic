from luatypes import TypeNumber, TypeNumberRange



class ArithmeticEvaluator:

        def impl_exit_binaryMathOp(self, node, function, lax=False):
                left_type = self.get_type(node.left)
                right_type = self.get_type(node.right)

                if not TypeNumber().coercible_from(left_type):
                        self.error(f"{left_type} not convertible to number", node.left)
                if not TypeNumber().coercible_from(right_type):
                        self.error(f"{right_type} not convertible to number", node.right)        

                lhs_num = left_type.get_single_number()
                rhs_num = right_type.get_single_number()

                if lhs_num is None or rhs_num is None:
                        self.set_type(node, TypeNumber())
                        return

                self.set_type(node, TypeNumberRange(function(lhs_num, rhs_num)))


        def exit_SubOp(self, node):
                self.impl_exit_binaryMathOp(node, lambda a, b: a - b)

        def exit_MultOp(self, node):
                self.impl_exit_binaryMathOp(node, lambda a, b: a * b)

        def exit_FloatDivOp(self, node):
                self.impl_exit_binaryMathOp(node, lambda a, b: a / b)

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
        
        def exit_UMinusOp(self, node):

                # if isinstance(left_type, TypeAny) or isinstance(right_type, TypeAny):
                #         return

                the_type = self.get_type(node.operand)

                if not TypeNumber().coercible_from(the_type):
                        self.error(f"{the_type} not convertible to number", node.operand)

                if isinstance(the_type, TypeNumber):
                        single = the_type.get_single_number()
                        if single is not None:
                                self.set_type(node, TypeNumber(-single))
                                return

                        if isinstance(the_type, TypeNumberRange):
                                self.set_type(node, TypeNumber(-the_type.max_value, -the_type.min_value))
                                return

                self.set_type(node, TypeNumber())

        def exit_ModOp(self, node):
                self.set_type(node, TypeNumber())

        def exit_ExpoOp(self, node):
                self.set_type(node, TypeNumber())

