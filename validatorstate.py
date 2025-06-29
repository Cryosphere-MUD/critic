
class ValidatorState:
        last_error = None

        def error(self, txt, node, level = "error"):

                tokennode = node

                line = ""

                if isinstance(node, list):
                        node = None

                if node and node.first_token:

                        before = self.source.rfind('\n', 0, node.first_token.start)
                        after = self.source.find('\n', node.first_token.start)

                        prefix = "    "
                        if after == -1:
                                line = prefix + self.source[before+1:]
                        else:
                                line = prefix + self.source[before+1:after]

                        extra = "\n" + prefix
                        for _ in range(before, node.first_token.start-1):
                                extra += " "

                        extra += "^"

                        for _ in range(node.first_token.start + 1, node.first_token.stop+1):
                                extra += "~"

                        line += extra

                args = (txt, node, level)
                if self.last_error == args:
                        return
                self.last_error = args

                self.error_handler(*args, line=line)
