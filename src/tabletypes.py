from luatypes import TypeBase, TypeTable, TypeAny

from pprint import pprint

class TypeStruct(TypeTable):

        def __init__(self, name, fields):
                self.id = name
                self.fields = fields
                self.missing_field_is_error = True

        def __str__(self):
                return "[" + self.id + "]"

        def __eq__(self, other):
                return type(self) == type(other) and self.id == other.name

        def __hash__(self):
                return hash((type(id), self.id))

        def check_field(self, fieldname):
                return self.fields.get(fieldname)

        def convertible_from(self, source):
                if isinstance(source, TypeAny):
                        return True

                return type(self) == type(source) and self.id == source.id
