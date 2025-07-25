from luatypes import TypeBool, TypeString, TypeStringKnownPrefix, TypeUnion, TypeTable, TypeNumberRange, TypeNumber, TypeAny, TypeStringKnownPrefixType, TypeNil, TypeUnionType


def global_static_assert(self, args):
	fmt = self.get_type(args[0])
	if fmt != TypeBool(True):
		self.error("static_assert false or ambiguous", args[0])


def global_string_format(self, args):
	fmt = self.get_type(args[0])
	values = list(fmt.strings())
	if len(values) == 1:
		if "%" not in values[0]:
			#self.error(f"Unnecessary call to string.format with {fmt}")
			return TypeString(values[0])
		
		arg_types = [self.get_type(arg) for arg in args[1:]]
		any_tainted = any(isinstance(arg, TypeString) and arg.tainted for arg in arg_types)

		return TypeStringKnownPrefix(values[0].split("%")[0], tainted=any_tainted)


def global_ipairs(self, args):
	typ = self.get_type(args[0])
	if isinstance(typ, TypeTable):
		if table := typ._table:
			min_key = min(table.keys())
			max_key = max(table.keys())
			values = TypeUnion(*table.values())
			return TypeNumberRange(min_value = min_key, max_value = max_key), values

		if typ.key and typ.value:
			return typ.key, typ.value

	return TypeNumber(), TypeAny()


def global_pairs(self, args):
	typ = self.get_type(args[0])
	if isinstance(typ, TypeTable):
		if table := typ._table:
			if typ.non_numeric:
				return TypeString(*list(table.keys())), TypeUnion(*table.values())
			min_key = min(table.keys())
			max_key = max(table.keys())
			values = TypeUnion(*table.values())
			return TypeNumberRange(min_value = min_key, max_value = max_key), values
		
		if typ.key and typ.value:
			return typ.key, typ.value

	return TypeAny(), TypeAny()



def global_tonumber(self, args):
	typ = self.get_type(args[0])
	if typ.get_single_number():
		return TypeNumber()

	return TypeUnion(TypeNil(), TypeNumber())
	
