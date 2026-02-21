import glob
from mudversion import get_bindings_glob
from bindingsparser import parse_bindings

from types import MappingProxyType

CLASS_METHODS = {}
MODULE_SYMBOLS = {}
BINDINGS = {}

for binding_filename in glob.glob(get_bindings_glob()):
        with open(binding_filename, "r") as file:
                result = parse_bindings(file)
                
                BINDINGS.update(result.globals)		
                MODULE_SYMBOLS.update(result.modules)
                
                for classname, methods in result.klasses.items():
                        CLASS_METHODS.setdefault(classname, {}).update(methods)
                
CLASS_METHODS = MappingProxyType(CLASS_METHODS)
MODULE_SYMBOLS = MappingProxyType(MODULE_SYMBOLS)
CLASS_METHODS = MappingProxyType(CLASS_METHODS)