import sys

got_error = False

errored_nodes = set()
error_fn = None

no_warnings = False

def error(txt, node = None, level = "error", line = None):

        if no_warnings and level == "warning":
                return

        if node:
                node = id(node)

        if node and node in errored_nodes:
                return

        if node:
                errored_nodes.add(node)

        fn_display = error_fn

        print(f"::{level}:: {fn_display} : {txt}", file=sys.stderr)

        if line:
                print(line)

        global got_error
        got_error = True

def set_no_warnings(new_value):
        global no_warnings
        no_warnings = new_value