import sys


got_error = False

errored_nodes = set()
error_fn = None

no_warnings = False

quiet = False

def had_error():
        return got_error

def set_no_warnings(new_value):
        global no_warnings
        no_warnings = new_value
        
def set_quiet(new_value):
        global quiet
        quiet = new_value

def clear_error():
        global got_error
        got_error = False

def set_filename(new_fn):
	global error_fn
	error_fn = new_fn

def error(txt, node = None, level = "error", line = None):
        global got_error
        got_error = True

        if quiet:
                return

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

