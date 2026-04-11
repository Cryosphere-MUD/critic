from luatypes import TypeBase, TypeString, TypeTable, TypeAny, TypeNumberRange, TypeWithFields, TypeBool

CHECK_MUDOBJECT_ID = None

def setValidator(validator):
        global CHECK_MUDOBJECT_ID
        CHECK_MUDOBJECT_ID = validator

class TypeMudObject(TypeBase, TypeWithFields):
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

                if isinstance(source, TypeString) and source.values:
                        for value in source.values:
                                if not CHECK_MUDOBJECT_ID(value):
                                        return False
                        return True
                        
                return super().convertible_from(source)

        def check_field(self, fieldname):

                if self.is_invoker and fieldname == "id":
                        return TypeString("@pl", tainted=False)

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
        
        def lookup_method(self, methodname):
                from bindings import CLASS_METHODS
                return CLASS_METHODS["mudobject"].get(methodname)

def represent_type(field):
        if type(field) == str:
                return TypeString(field, tainted = False)
        if type(field) == bool:
                return TypeBool(field)
        if type(field) == int:
                return TypeNumberRange(field)

        if type(field) == list:
                map = {}
                for i, v in enumerate(field):
                        map[i + 1] = represent_type(v)
                return TypeTable(map)
                                
        if type(field) == dict:
                map = {}
                for i, v in field.items():
                        map[i] = represent_type(v)
                return TypeTable(map)

        assert False


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

        def combine_types(self, types):
                for t in types:
                        if isinstance(t, TypeMudObject) and not isinstance(t, TypeSpecificMudObject):
                                return t
                return self

        def check_treatas_field(self, fieldname):
                if fieldname[0] == '!':
                        return TypeAny()
                if fieldname[0] == '$':
                        return TypeAny()

                if fieldname in self.mudobject:
                        return represent_type(self.mudobject.get(fieldname))
                
                treatas = self.mudobject.get("treatas")
                if treatas:
                        if isinstance(treatas, list):
                                for treatas_member in treatas:
                                        treatas_obj = CHECK_MUDOBJECT_ID(treatas_member)
                                        if treatas_obj:
                                                if TypeSpecificMudObject(treatas_obj).check_treatas_field(fieldname):
                                                        return True
                        else:
                                treatas_obj = CHECK_MUDOBJECT_ID(treatas)
                                if treatas_obj:
                                        if TypeSpecificMudObject(treatas_obj).check_treatas_field(fieldname):
                                                return True

                for i in range(self.mudobject.get("treatas.count", 0)):
                        treatas = self.mudobject.get("treatas." + str(i))
                        if treatas:
                                treatas_obj = CHECK_MUDOBJECT_ID(treatas)
                                if treatas_obj:
                                        if TypeSpecificMudObject(treatas_obj).check_treatas_field(fieldname):
                                                return True


        def check_field(self, fieldname):
                
                if fieldname in self.mudobject:
                        field = represent_type(self.mudobject[fieldname])
                        return field
                
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


