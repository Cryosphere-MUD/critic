#!/usr/bin/python

import os, sys

from luatypes import TypeFunction, TypeAny, TypeModule, TypeNumber, TypeString, TypeNil, TypeBool, TypeNilString, TypeTable, TypeUnionType, TypeKey, TypeZoneTag, TypeEventName, TypeUnion, TypeNumberRange
from mudtypes import TypeMudObjectOrID, TypeMudObject
from tabletypes import TypeStruct

module = None

def set_module(module_id):
        global module
        module = module_id


basic_types = {
        "eventname": TypeEventName,
        "nil": TypeNil
}



struct_types = {
}

global_symbols = {
}


def conv_type(argtype, isarg = False):

        argtype = argtype.strip()

        if constructor := basic_types.get(argtype):
                return constructor()

        if "|" in argtype:
                return TypeUnion(*[conv_type(arg, isarg) for arg in argtype.split("|")])
        
        if argtype == "any":
               return TypeAny()
        
        if len(argtype) > 1 and argtype[0] == '\"' and argtype[-1] == '\"':
                return TypeString(argtype[1:-1])
        
        if argtype.isnumeric():
                num = int(argtype)
                return TypeNumberRange(num, num)

        if struct := struct_types.get(argtype):
                return struct

        if argtype.startswith("object") or argtype.startswith("player"):
                if isarg:
                        return TypeMudObjectOrID()
                return TypeMudObject()
        elif argtype.startswith("nilobject"):
                if isarg:
                        return TypeUnionType(TypeMudObjectOrID(), TypeNil())
                return TypeUnionType(TypeMudObject(), TypeNil())
        elif argtype == "stringvector":
                return TypeTable(key=TypeNumber(), value=TypeString())
        elif argtype.startswith("string") or argtype == "char":
                return TypeString(tainted=True)
        elif argtype.startswith("nilstring"):
                if isarg:
                        return TypeNilString()
                else:
                        return TypeString(tainted=True)
        elif argtype.startswith("int") or argtype.startswith("flag") or argtype.startswith("priv"):
                return TypeNumber()
        elif argtype.startswith("float"):
                return TypeNumber()
        elif argtype == "void":
                if isarg:
                        return TypeAny()
                else:
                        return TypeNil()
        elif argtype.startswith("bool"):
                return TypeBool()
        elif argtype.startswith("untainted"):
                return TypeString(tainted=False)
        elif argtype.startswith("filter") or argtype.startswith("function"):
                return TypeAny()
        elif argtype in ("set", "vector", "objset", "objvector", "world"):
                return TypeTable(key=TypeNumber(), value=TypeMudObject())
        elif argtype == "table":
                return TypeTable()
        elif argtype == "nil|int":
                return TypeUnionType(TypeNumber(), TypeNil())
        elif argtype.startswith("zonetag"):
                return TypeZoneTag()
        elif argtype.startswith("key"):
                return TypeKey()
        else:
                print(argtype)
                exit(1)
                return TypeAny()



def parse_bindings(file):

        methods = {}
        modules = {}

        module_fns = {}

        global module
        module = None

        globals = []

        global_fns = {}

        klass_fns = {}

        def handle_decl(decl):

                decl = decl.lower()

                attributes = []

                if "] " in decl:
                        attstr, decl = decl.split(" ", 1)
                        assert attstr[0:2] == "[[" and attstr[-2:] == "]]"
                        attstr = attstr[2:-2]
                        attributes = attstr.split(",")

                return_type, rest = decl.split(" ", 1)
                name, args_part = rest.split("(")
                args = args_part.strip()[:-1].split(",")

                klass = None

                if ":" in name:
                        klass, name = name.split(":")

                args = [arg for arg in args if arg]

                def build_argtypes(method):
                        min_args = 0
                        max_args = 0
                        arg_types = []
                        var_args = False

                        for i, arg in enumerate(args):
                                max_args += 1

                                arg = arg.strip()
                                argtype, argname = arg.rsplit(" ", 1)

                                if ":" in argname:
                                        argname, _ = argname.split(":")
                                        is_optional = "?"
                                else:
                                        min_args += 1

                                if argname == "varargs":
                                        var_args = True
                                
                                if argtype.endswith("..."):
                                        var_args = True
                                        argtype = argtype[0:-3]

                                if name == "set" and i == 2:
                                        arg_types.append(TypeAny()) # hardcoded overloading
                                else:
                                        arg_types.append(conv_type(argtype, isarg=True))

                                #tl_args.append(argname + is_optional + ": " + the_type)
                        
                        tf = TypeFunction(name=name, min_args=min_args, max_args=max_args, args=arg_types, varargs=var_args, return_type = 
                                            conv_type(return_type))
                        
                        if module:
                                tf.module = module

                        tf.no_return = "noreturn" in attributes

                        return tf


                if klass:
                        fn = build_argtypes(args)
                        fn.name = name
                        
                        if klass not in klass_fns:
                                klass_fns[klass] = {}
                        klass_fns[klass][name] = fn

                if module is None:
                        fn = build_argtypes(args)
                        fn.name = name
                        fn.is_global = True

                        global_fns[name] = fn

                else:
                        if module not in module_fns:
                                module_fns[module] = TypeModule()

                        fn = build_argtypes(args)
                        fn.name = name

                        module_fns[module].add(name, fn)

                        #module_fns.setdefault(module, []).append(name)

        def handle_struct_defn(name, defns):
                fields = {}
                for l in defns.split("\n"):
                        l = l.strip()
                        if not l:
                                continue
                        if l[-1] == ";":
                                l = l[:-1]
                        type, field = l.rsplit(" ", 1)
                        fields[field] = conv_type(type, False)
                name = name.strip()

                if name in struct_types:
                        struct_types[name].fields = fields
                else:
                        struct_types[name] = TypeStruct(name, fields)

        def handle_type_defn(arg):
                name, defn = arg.split("=")
                struct_types[name.strip()] = conv_type(defn.strip(), False)

        def handle_global(arg):
                if arg[-1] == ";":
                        arg = arg[:-1]
                type, name = arg.rsplit(" ", 1)
                
                if module:
                        if module not in module_fns:
                                module_fns[module] = TypeModule()

                        module_fns[module].add(name, conv_type(type.strip(), False))

                else:

                        global_fns[name.strip()] = conv_type(type.strip(), False)

        incpp = False
        defining_struct = None
        struct_defn = ""

        try:
                for line in file:

                        if incpp:
                                if line == "}\n":
                                        incpp = False
                                        continue
                                continue

                        if defining_struct:
                                if line == "}\n" or line == "};\n":
                                        handle_struct_defn(defining_struct, struct_defn)
                                        defining_struct = False
                                        continue
                                struct_defn += line
                                continue

                        line = line.strip()

                        if not line:
                                continue
                        if line[0] == '#':
                                continue

                        if line[0:7] == "module ":
                                set_module(line[7:])
                                continue
                        if line[0:6] == "module":
                                continue

                        if line[0:7] == "struct ":
                                if "{" in line:
                                        defining_struct = line[7:].split("{")[0]
                                        struct_defn = ""
                                else:
                                        handle_struct_defn(line[7:], "")
                                continue

                        if line[0:5] == "type ":
                                handle_type_defn(line[5:])
                                continue

                        if line[0:7] == "global ":
                                handle_global(line[7:])
                                continue

                        if "=" in line:
                                decl, defn = line.split("=", 1)
                        else:
                                decl = line
                                defn = ""

                        handle_decl(decl)

                        defn = defn.strip()

                        if defn == "{":
                                incpp = True


        except EOFError:

                pass

        return global_fns, module_fns, klass_fns


