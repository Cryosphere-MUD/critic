CHECK_MUDOBJECT_ID = None


def setValidator(validator):
        global CHECK_MUDOBJECT_ID
        CHECK_MUDOBJECT_ID = validator



class TypeBase:
        global_assert = False
        is_global = False
        module = ""
        is_invoker = False
        deferred_validate = False

        def convertible_from(self, source):
                if isinstance(source, TypeAny):
                        return True

                if isinstance(source, TypeUnionType):
                        for source_sub in source.types():
                                if not self.convertible_from(source_sub):
                                        return False
                        return True

                return False

        def difference(self, other):
                if self == other:
                        return TypeNil()
                return self

        def get_single_number(self):
                return None

        def denil(self):
                return self

        def union(self, other):
                return TypeUnion(self, other)
        
        def types(self):
                return [self]

        def __str__(self):
                return str(type(self))

        def __repr__(self):
                return f"<{str(self)}>"
        
        def strings(self):
                return []


class TypeAny(TypeBase):
        def __str__(self):
                return "any"

        def difference(self, _other):
                return self

        def __eq__(self, other):
                return type(self) == type(other)
        
        def __hash__(self):
                return hash((type(self)))

        def convertible_from(self, source):
                return True

TypeInvalid = TypeAny


class TypeNil(TypeBase):
        def __str__(self):
                return "nil"

        def difference(self, other):
                if type(other) == TypeNil:
                        return TypeInvalid()
                return self

        def convertible_from(self, source):
                if type(self) == type(source):
                        return True

        def denil(self):
                # maybe this should throw? or return a special TypeNothing??? not sure.
                return TypeInvalid()

        def __eq__(self, other):
                return type(self) == type(other)

        def __hash__(self):
                return hash((type(self)))

class TypeModule(TypeBase):
        def __init__(self, *unchecked):
                self._values = {}
                for n in unchecked:
                        self._values[n] = TypeAny()

        def contains(self, rhs):
                return rhs in self._values
        
        def lookup(self, rhs):
                return self._values.get(rhs)
        
        def add(self, arg1, arg2 = None):
                if arg2 is None:
                        self._values[arg1.name] = arg1
                else:
                        self._values[arg1] = arg2

class SymbolUncheckedModule(TypeBase):
        def contains(self, rhs):
                return True


class CapitalsModule(TypeModule):
        def __init__(self, *values):
                if values and isinstance(values[0], dict):
                        super().__init__()
                        for key, value in values[0].items():
                                self._values[key] = value
                        return

                super().__init__(*[value.upper() for value in values])

        def contains(self, rhs):
                return super().contains(rhs.upper())
        
        def lookup(self, rhs):
                return super().lookup(rhs.upper())


class AnyModule(TypeModule):
        def __init__(self):
                super().__init__()


class TypeBool(TypeBase):
        def __init__(self, value = None):
                self.value = value

        def __eq__(self, other):
                return type(self) == type(other) and self.value == other.value

        def __hash__(self):
                return hash((type(self), self.value))

        def bools(self):
                if self.value in (None, False):
                        yield False
                if self.value in (None, True):
                        yield True

        def __str__(self):
                if self.value is None:
                        return "bool"
                if self.value:
                        return "true"
                if not self.value:
                        return "false"

        def convertible_from(self, source):
                if type(self) == type(source):
                        return True

                if isinstance(source, TypeNumber):
                        return True

                return super().convertible_from(source)


class TypeTable(TypeBase):
        def __init__(self, table = None, non_numeric = False, key = None, value = None):
                self._table = table or None
                self.non_numeric = non_numeric
                self.key = key
                self.value = value

        def items(self):
                if self._table is None:
                        return ()
                return self._table.items()

        def __eq__(self, other):
                return (type(self) == type(other) and
                        hash(tuple(self.items())) == hash(tuple(other.items())))

        def __hash__(self):
                if self._table:
                        return hash((type(self), tuple(self.items())))
                return hash(type(self))

        def __str__(self):
                if table := self._table:
                        return f"table[{len(table)}]"
                return "table"

        def convertible_from(self, source):
                if type(self) == type(source):
                        return True
                
                return super().convertible_from(source)
                

class TypeMap(TypeBase):
        def __init__(self, values):
                self.values = values

        def get_member(self, member_name):
                return self.values.get(member_name, TypeNil())


class TypeMudObject(TypeBase):
        def __init__(self, invoker = False):
                self.is_invoker = invoker

        def __str__(self):
                if self.is_invoker:
                        return "invoker"
                else:
                        return "mudobject"

        def __eq__(self, other):
                return type(self) == type(other) and self.is_invoker == other.is_invoker

        def __hash__(self):
                return hash((type(self), self.is_invoker))

        def difference(self, _other):
                return self

        def convertible_from(self, source):
                if type(self) == type(source):
                        return True

                if isinstance(source, TypeSpecificMudObject):
                        return True

                return super().convertible_from(source)

        def check_field(self, fieldname):

                if fieldname in ("id", "short"):
                        return TypeString(tainted=False)
                        
#                import schema
#                if field_type := schema.validate_key(fieldname):
                        # the dump of the schema doesn't contain the actual metadata
                        # because it's all hidden in lua closures.
#                        return TypeAny()

                if fieldname[0] == '!':
                        return TypeAny()
                if fieldname[0] == '$':
                        return TypeAny()
                 
                return TypeAny()


class TypeSpecificMudObject(TypeMudObject):
        def __init__(self, mudobject):
                self.mudobject = mudobject
                self.id = mudobject["id"]

        def __hash__(self):
                return hash((type(self), self.id))

        def __eq__(self, other):
                return type(self) == type(other) and self.id == other.id

        def __str__(self):
                return f"mudobject:{self.id}"

        def check_treatas_field(self, fieldname):
                if fieldname[0] == '!':
                        return TypeAny()
                if fieldname[0] == '$':
                        return TypeAny()
                if fieldname in self.mudobject:
                        field = self.mudobject[fieldname]
                        if type(field) == str:
                                return TypeString(field)
                        if type(field) == int:
                                return TypeNumberRange(field)
                        return TypeAny()
                
                treatas = self.mudobject.get("treatas")
                if treatas:
                        treatas_obj = CHECK_MUDOBJECT_ID(treatas)
                        if treatas_obj:
                                return TypeSpecificMudObject(treatas_obj).check_treatas_field(fieldname)
                        print(f"invalid treatas {treatas}")
                        exit(1)


        def check_field(self, fieldname):

                if fieldname in self.mudobject:
                        field = self.mudobject[fieldname]
                        if type(field) == str:
                                return TypeString(field, tainted = False)
                        if type(field) == int:
                                return TypeNumberRange(field)
                        return TypeAny()
                
                return super().check_field(fieldname)


class TypeMudObjectOrID(TypeBase):

        def __str__(self):
                return "mudobject | valid_id";

        def convertible_from(self, source):
                if type(self) == type(source):
                        return True
                if type(source) == TypeMudObject:
                        return True
                if type(source) == TypeSpecificMudObject:
                        return True
                
                if isinstance(source, TypeTable):
                        # XXX hack for verbs that reassign to table
                        return True

                if type(source) == TypeString:
                        if len(source.values):
                                return all(CHECK_MUDOBJECT_ID(value) for value in source.values)
                        return True

                return super().convertible_from(source)


class TypeNumber(TypeBase):
        def __init__(self, *values):
                self.values = list(values)

        def __str__(self):
                return "number"

        def __hash__(self):
                return hash((type(self), tuple(self.values)))

        def __eq__(self, other):
                return type(self) == type(other) and self.values == other.values

        def convertible_from(self, source):
                if type(self) == type(source):
                        return True

                if type(source) == TypeNumberRange:
                        return True

                return super().convertible_from(source)


class TypeNumberRange(TypeNumber):
        def __init__(self, min_value, max_value = None):
                self.min_value = min_value
                self.max_value = max_value if max_value is not None else min_value

        def __str__(self):
                if self.min_value == self.max_value:
                        return str(self.min_value)
                return f"number({self.min_value} to {self.max_value})"

        def __hash__(self):
                return hash((type(self), self.min_value, self.max_value))

        def __eq__(self, other):
                return type(self) == type(other) and self.min_value == other.min_value and self.max_value == other.max_value

        def get_single_number(self):
                if self.min_value == self.max_value:
                        return self.min_value

        def types(self):
                return [TypeNumberRange(value) for value in range(self.min_value, self.max_value)]

        def convertible_from(self, source):
                if type(self) == type(source):
                        return True
                
                return super().convertible_from(source)


class TypeString(TypeBase):
        def __init__(self, *values, tainted = True):
                self.values = list(values)
                self.tainted = tainted

        def __eq__(self, other):
                return (type(self) == type(other) and
                        self.values == other.values and
                        self.tainted == other.tainted)

        def __hash__(self):
                return hash((type(self), tuple(self.values), type(self.tainted)))

        def __str__(self):
                if self.values:
                        return " | ".join(repr(value) for value in self.values)
                if self.tainted:
                        return "string(tainted)"
                return "string(untainted)"

        def types(self):
                if self.values:
                        return [TypeString(value) for value in self.values]
                return [self]

        def strings(self):
                yield from self.values

        def convertible_from(self, source):
                if isinstance(source
                              , TypeString) and (self.tainted or (self.tainted == source.tainted)):
                        return True

                if isinstance(source, TypeNumber):
                        return True
        
                return super().convertible_from(source)


class TypeTranslatedString(TypeString):
        def __str__(self):
                return "[translated]" + super().__str__()
        


class TypeKey(TypeBase):
        def __str__(self):
                return "key"

        def convertible_from(self, source):
                if type(source) == TypeAny:
                        return True

                if isinstance(source, TypeString):
                        if not source.values:
                                return True

                        for key in source.values:
                                if not key:
                                        return False

                        return True

                return False


class TypeConstrainedString(TypeString):
        def __str__(self):
                return "constrained_string"

        def convertible_from(self, source):
                if type(source) == type(self):
                        return True

                if type(source) == TypeAny:
                        return True
                
                if isinstance(source, TypeString):
                        if not source.values:
                                return self.test_stringtype_validity(source)

                        return all(self.test_string_validity(specific) for specific in source.values)

                return False

        def test_stringtype_validity(self, source):
                # by default let unknown strings go through
                return True


class TypeZoneTag(TypeConstrainedString):
        def __str__(self):
                return "zonetag"

        def __init__(self):
                super().__init__(tainted=False)

        def test_string_validity(self, value):
                from universe import valid_zonetags
                return value in valid_zonetags



class TypeEventName(TypeConstrainedString):
        def __str__(self):
                return "eventname"

        def __init__(self):
                super().__init__(tainted=False)

        def test_string_validity(self, value):
                from events import check_valid_event
                return check_valid_event(value)

        def test_stringtype_validity(self, source):
                from events import check_valid_event
                if isinstance(source, TypeStringKnownPrefix):
                        # if this is a known prefix string then it presumably ought
                        # to be something like tell.* which will pass this check
                        return check_valid_event(source.known_prefix)
                return super().test_stringtype_validity(source)


class TypeStringKnownPrefix(TypeString):
        def __init__(self, known_prefix, tainted):
                self.known_prefix = known_prefix
                self.tainted = tainted
                self.values = []

        def __str__(self):
                return ("[tainted]" if self.tainted else "[untainted]") + repr(self.known_prefix) + "..."

        def __eq__(self, other):
                return (type(self) == type(other) and
                        self.known_prefix == other.known_prefix)

        def __hash__(self):
                return hash((type(self), tuple(self.known_prefix)))


class TypeUnionType(TypeBase):
        def __init__(self, *types):
                self._types = set(types)
                assert len(self._types) > 1

        def types(self):
                return self._types

        def __eq__(self, other):
                return hash(self) == hash(other)

        def __hash__(self):
                hashes = [hash(part) for part in self._types]
                return hash((type(self), tuple(sorted(hashes))))

        def union(self, type):
                return TypeUnion(*self._types, type)
        
        def __str__(self):
                return " | ".join(str(type) for type in self._types)

        def denil(self):
                denilled = set(filter(lambda f: not isinstance(f, TypeNil), self._types))
                if len(denilled) == len(self._types):
                        return self
                if len(denilled) == 1:
                        return list(denilled)[0]
                return TypeUnionType(*denilled)

        def difference(self, other):
                if isinstance(other, TypeUnionType):
                        to_remove = set(other._types)
                else:
                        to_remove = {other}

                result = [t for t in self._types if t not in to_remove]

                if not result:
                        return TypeNil()

                if len(result) == 1:
                        return result[0]

                return TypeUnionType(*result)

        def convertible_from(self, source):
                for t in self._types:
                        if t.convertible_from(source):
                                return True
                return super().convertible_from(source)

def TypeNilString():
        return TypeUnionType(TypeString(tainted=True), TypeNil())

#class TypeNilString(TypeBase):
#
#        def convertible_from(self, source):
#                if type(source) == TypeNilString:
#                        return True#
#
#                if type(source) == TypeString:
#                        return True
#
#                return super().convertible_from(source)


class TypeFunction(TypeBase):
        def __init__(self, *, name, min_args = None, max_args = None, args, varargs = False, return_type = None, no_return = False):
                if min_args is None:
                        min_args = len(args)
                if max_args is None:
                        max_args = len(args)
                self.name = name
                self.min_args = min_args
                self.max_args = max_args
                self.args = args
                self.varargs = varargs
                self.return_type = return_type or TypeAny()
                self.no_return = no_return
                self.visiting_from_call = 0

        def __str__(self):
                args = "(" + ", ".join(str(arg) for arg in self.args) + ")"
                if self.name:
                        return f"function {self.name}{args}"
                return "function{args}"

        def validate_argcount(self, argcount):
                if self.varargs:
                        return True
                return argcount >= self.min_args and argcount <= self.max_args
        
        def get_argtype(self, argno):
                if self.varargs and argno >= len(self.args):
                        return TypeAny()
                return self.args[argno]


def TypeFunctionAny(*, name):
        return TypeFunction(name=name, min_args=0, max_args=0, varargs=True, args=[])


def TypeUnion(*args):
        for t in args:
                assert isinstance(t, TypeBase)

        if any(isinstance(t, TypeAny) for t in args):
                return TypeAny()

        type_set = set()
        string_values = set()
        mud_objects = set()
        bool_values = set()
        any_string = False
        any_mudobject = False
        string_tainted = False

        def add(t):
                nonlocal string_tainted
                if isinstance(t, TypeUnionType):
                        for subtype in t.types():
                                add(subtype)
                elif isinstance(t, TypeString):
                        string_tainted |= t.tainted
                        if t.values:
                                string_values.update(t.values)
                        else:
                                nonlocal any_string
                                any_string = True
                elif isinstance(t, TypeSpecificMudObject):
                        mud_objects.add(t)
                elif isinstance(t, TypeBool):
                        nonlocal bool_values
                        bool_values |= set(t.bools())
                elif isinstance(t, TypeMudObject):
                        nonlocal any_mudobject
                        any_mudobject = True
                else:
                        type_set.add(t)

        for arg in args:
                add(arg)

        if any_mudobject:
                type_set.add(TypeMudObject())
        else:
                for mo in mud_objects:
                        type_set.add(mo)

        if bool_values:
                if len(bool_values) == 2:
                        type_set.add(TypeBool())
                else:
                        type_set.add(TypeBool(list(bool_values)[0]))

        if any_string:
                type_set.add(TypeString(tainted=string_tainted))
        elif string_values:
                type_set.add(TypeString(*string_values, tainted=string_tainted))

        if len(type_set) == 1:
                return next(iter(type_set))
        
        return TypeUnionType(*type_set)
