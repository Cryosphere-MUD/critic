import glob
from mudversion import get_bindings_glob
from bindingsparser import parse_bindings

from types import MappingProxyType

CLASS_METHODS = {}
MODULE_SYMBOLS = {}
BINDINGS = {}

for binding_filename in glob.glob(get_bindings_glob()):
        with open(binding_filename, "r") as file:
                bindings, modules, klass = parse_bindings(file)
                BINDINGS.update(bindings)		
                MODULE_SYMBOLS.update(modules)
                
                for classname, methods in klass.items():
                        CLASS_METHODS.setdefault(classname, {}).update(methods)
                
CLASS_METHODS = MappingProxyType(CLASS_METHODS)
MODULE_SYMBOLS = MappingProxyType(MODULE_SYMBOLS)
CLASS_METHODS = MappingProxyType(CLASS_METHODS)