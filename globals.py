from luatypes import CapitalsModule, TypeNumber, TypeAny, TypeModule, TypeFunction, TypeString, TypeBool, TypeFunctionAny, TypeUnion, TypeNil, TypeTable, TypeNotNil
from mudtypes import TypeMudObjectOrID

from mudglobals import register_mud_global_scope
from mudversion import is_musicmud, is_aardmud

GLOBAL_SYMBOLS = ("pairs", "ipairs", "explode", "loadstring", "strbyte", 
                  "pcall", "unpack", "next", "xpcall", "load")

def MakeMathModule():
        math = TypeModule("math")

        def TypeNumberOrString():
                return TypeUnion(TypeNumber(), TypeString())

        math.add(TypeFunction(name="max", args=[TypeNumberOrString(), TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="min", args=[TypeNumberOrString(), TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="fmod", args=[TypeNumberOrString(), TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="pow", args=[TypeNumberOrString(), TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="ceil", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="floor", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="abs", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="log10", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="log", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="sqrt", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="cos", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="sin", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="tan", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="rad", args=[TypeNumberOrString()], return_type=TypeNumber()))
        math.add(TypeFunction(name="random", args=[TypeNumberOrString(), TypeNumberOrString()], return_type=TypeNumber(), min_args=1))
        math.add("huge", TypeNumber())
        return math

def MakeTableModule():
        table = TypeModule("table")
        table.add(TypeFunction(name="insert", args=[TypeTable(), TypeAny(), TypeAny()], min_args=2))
        table.add(TypeFunction(name="concat", args=[TypeTable(), TypeString(), TypeNumber(), TypeNumber()], return_type=TypeString(), min_args=1))
        table.add(TypeFunction(name="remove", args=[TypeTable(), TypeNumber()]))
        table.add(TypeFunction(name="sort", args=[TypeTable(), TypeAny()], min_args=1))
        table.add(TypeFunction(name="copy", args=[TypeTable()], return_type=TypeTable(), min_args=1))
        table.add(TypeFunction(name="size", args=[TypeTable()], return_type=TypeNumber(), min_args=1))
        table.add(TypeFunctionAny(name="unpack"))
        return table

def MakeStringModule():
        type = TypeModule("string")
        type.add(TypeFunction(name="len", args=[TypeNotNil()], return_type=TypeNumber()))
        # these should preserve taint
        type.add(TypeFunction(name="sub", args=[TypeString(), TypeNumber(), TypeNumber()], return_type=TypeString(tainted=False), min_args=2))
        type.add(TypeFunction(name="find", args=[TypeString(), TypeString(), TypeNumber(), TypeBool()], return_type=TypeUnion(TypeNil(), TypeNumber()), min_args=2))
        type.add(TypeFunction(name="rep", args=[TypeString(), TypeNumber()], return_type=TypeString()))
        type.add(TypeFunction(name="byte", args=[TypeString(), TypeNumber()], return_type=TypeNumber(), min_args=1))
        
        string_format = TypeFunctionAny(name="format")
        string_format.module = "string"

        type.add(string_format)
        type.add(TypeFunctionAny(name="gsub"))
        type.add(TypeFunctionAny(name="reverse"))
        type.add(TypeFunctionAny(name="char"))
        type.add(TypeFunctionAny(name="upper"))
        type.add(TypeFunction(name="lower", args=[TypeString()], return_type=TypeString()))
        type.add(TypeFunctionAny(name="match"))
        type.add(TypeFunctionAny(name="gmatch"))
        return type


def make_global_scope(bindings_global):

        global_scope = {}
        global_scope.update(bindings_global)

        global_scope["math"] = MakeMathModule()
        global_scope["table"] = MakeTableModule()
        global_scope["string"] = MakeStringModule()

        if is_musicmud():
                register_mud_global_scope(global_scope)

        global_assert = TypeFunction(name="assert", args=[TypeAny()])
        global_assert.global_assert = True

        global_scope["assert"] = global_assert

        global_print = TypeFunction(name="print", args=[TypeAny()])

        def register_global(symbol):
                symbol.is_global = True
                global_scope[symbol.name] = symbol

        register_global(global_print)

        register_global(TypeFunction(name="static_assert", args=[TypeAny()]))
        register_global(TypeFunction(name="tostring", args=[TypeAny()], return_type=TypeString()))
        register_global(TypeFunction(name="tonumber", args=[TypeAny()], return_type=TypeUnion(TypeNumber(), TypeNil())))
        
        for symbol in GLOBAL_SYMBOLS:
                global_scope[symbol] = TypeFunctionAny(name=symbol)
                global_scope[symbol].is_global = True
                
        return global_scope