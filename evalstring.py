from luatypes import TypeString, TypeTranslatedString, TypeNumberRange, TypeStringKnownPrefix, TypeNumber

class StringEvaluator:

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

