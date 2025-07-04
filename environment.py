from luatypes import CapitalsModule, TypeNumber, TypeAny, TypeModule, TypeFunction, TypeString, TypeBool, TypeFunctionAny, TypeUnion, TypeNil, TypeTable
from mudtypes import TypeMudObjectOrID

from universe import valid_quests, valid_minis, valid_sims

valid_flags = {}

with open("../data/flags", "r") as file:
        for idx, f in enumerate(file):
                valid_flags[f.strip().split(" ")[0].upper()] = TypeNumber(idx + 1)

valid_pflags = {}

with open("../data/pflags", "r") as file:
        for idx, f in enumerate(file):
                valid_pflags[f.strip().split(" ")[0].upper()] = TypeNumber(idx + 1)

UNCHECKED_MODULES = []
UNCHECKED_MODULES.append("coroutine")
UNCHECKED_MODULES.append("trace")
UNCHECKED_MODULES.append("coroutines")
UNCHECKED_MODULES.append("json")
UNCHECKED_MODULES.append("Array")
UNCHECKED_MODULES.append("attributes")
UNCHECKED_MODULES.append("match") # matcher bitflags

GLOBAL_SYMBOLS = ("pairs", "import", "ipairs", "tonumber", "explode", "loadstring", "clone", "strbyte", 
                       "airtight_rooms", "sendrg", "tostring", "check_syntax", "pcall", "rawget", "get_max_opcount", "get_opcount", "unpack",
"proxy_table", "next", "get_route", "xpcall", "load")

def MakeMathModule():
        math = TypeModule()

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
        table = TypeModule()
        table.add(TypeFunction(name="insert", args=[TypeTable(), TypeAny(), TypeAny()], min_args=2))
        table.add(TypeFunction(name="concat", args=[TypeTable(), TypeString(), TypeNumber(), TypeNumber()], return_type=TypeString(), min_args=1))
        table.add(TypeFunction(name="remove", args=[TypeTable(), TypeNumber()]))
        table.add(TypeFunction(name="sort", args=[TypeTable(), TypeAny()], min_args=1))
        table.add(TypeFunction(name="copy", args=[TypeTable()], return_type=TypeTable(), min_args=1))
        table.add(TypeFunction(name="size", args=[TypeTable()], return_type=TypeNumber(), min_args=1))
        table.add(TypeFunctionAny(name="unpack"))
        return table

def make_global_scope(bindings_global):

        global_scope = {}
        global_scope.update(bindings_global)

        global_scope["math"] = MakeMathModule()

        global_scope["table"] = MakeTableModule()

        global_scope["priv"] = CapitalsModule(valid_pflags)
        global_scope["flag"] = CapitalsModule(valid_flags)

        global_scope["quest"] = CapitalsModule(valid_quests)
        global_scope["mini"] = CapitalsModule(valid_minis)
        global_scope["sim"] = CapitalsModule(valid_sims)

        global_scope["stance"] = CapitalsModule("STANDING", "SITTING", "LYING", "SWIMMING", "FLYING")

        for module in UNCHECKED_MODULES:
                global_scope[module] = TypeAny()

        global_scope["rank"] = CapitalsModule("POfficer", "Crewman", "commander", "Captain", "Commodore")
        
        global_scope["string"] = TypeModule()
        global_scope["string"].add("len", TypeFunction(name="len", args=[TypeAny()], return_type=TypeNumber()))
        # these should preserve taint
        global_scope["string"].add("sub", TypeFunction(name="sub", args=[TypeString(), TypeNumber(), TypeNumber()], return_type=TypeString(tainted=False), min_args=2))
        global_scope["string"].add("find", TypeFunction(name="find", args=[TypeString(), TypeString(), TypeNumber(), TypeBool()], return_type=TypeUnion(TypeNil(), TypeNumber()), min_args=2))
        global_scope["string"].add("rep", TypeFunction(name="rep", args=[TypeString(), TypeNumber()], return_type=TypeString()))
        global_scope["string"].add("byte", TypeFunction(name="byte", args=[TypeString(), TypeNumber()], return_type=TypeNumber(), min_args=1))
        
        string_format = TypeFunctionAny(name="format")
        string_format.module = "string"

        global_scope["string"].add("format", string_format)
        global_scope["string"].add("gsub", TypeFunctionAny(name="gsub"))
        global_scope["string"].add("char", TypeFunctionAny(name="char"))
        global_scope["string"].add("upper", TypeFunctionAny(name="upper"))
        global_scope["string"].add("lower", TypeFunction(name="lower", args=[TypeString()], return_type=TypeString()))
        global_scope["string"].add("match", TypeFunctionAny(name="match"))
        global_scope["string"].add("gmatch", TypeFunctionAny(name="gmatch"))

        global_scope["util"].add("explode", TypeAny())
        global_scope["util"].add(TypeFunction(name="colour_reverse", args=[TypeString()], return_type=TypeString()))
        global_scope["util"].add("colour_trim", TypeAny())
        global_scope["util"].add("formatitime", TypeAny())

        global_scope["cash"].add("match", TypeAny())

        global_scope["mud"].add("planet_objects", TypeFunctionAny(name="planet_objects"))
        global_scope["mud"].add("is_planet", TypeFunctionAny(name="is_planet"))

        global_assert = TypeFunction(name="assert", args=[TypeAny()])
        global_assert.global_assert = True

        global_scope["assert"] = global_assert

        global_print = TypeFunction(name="print", args=[TypeAny()])
        global_print.global_assert = True

        global_scope["print"] = global_print

        global_scope["lock"] = TypeFunction(name="lock", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        global_scope["open"] = TypeFunction(name="open", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        global_scope["close"] = TypeFunction(name="close", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        global_scope["pressurise"] = TypeFunction(name="pressurise", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)
        global_scope["depressurise"] = TypeFunction(name="depressurise", args=[TypeMudObjectOrID(), TypeAny()], min_args=1)

        global_scope["plural"] = TypeFunction(name="plural", args=[TypeAny()], return_type=TypeBool())

        global_scope["error"] = TypeFunction(name="error", args=[TypeString()], min_args=0, no_return=True)

        for symbol in GLOBAL_SYMBOLS:
                global_scope[symbol] = TypeFunctionAny(name=symbol)
                global_scope[symbol].is_global = True

        return global_scope