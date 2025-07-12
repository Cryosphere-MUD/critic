from luatypes import TypeString, TypeAny, TypeUnionType, TypeNil, TypeUnion, TypeNumberRange, TypeNumber, TypeStringKnownPrefix, TypeTable, TypeZoneTag, TypeTranslatedString, AnyModule
from mudtypes import TypeMudObject, TypeSpecificMudObject
import json
from spellcheck import spellcheck
from events import check_valid_event
from extrachunk import add_extra_chunk, ExtraChunk

def test_ancestor_flag(obj, flag):
        flags = obj.get("flags")

        if flags and flag in flags:
                return True
        
        start = obj.get("start")
        if not start:
                return False

        from mudtypes import CHECK_MUDOBJECT_ID

        parent = CHECK_MUDOBJECT_ID(start)
        if parent == True:
                return False
        
        if parent:
                return is_abstract(parent)
        
        return None


def global_effect_addtimer(self, args):
	s = self.get_type(args[1])
	got_any = False
	for value in s.strings():
		add_extra_chunk(ExtraChunk(lua=value))
		got_any = True

	# if not got_any:
	# 	self.error("unable to fully evaluate executed string here", args[1])


def global_effect_spawn_plain(self, args):
	s = self.get_type(args[4])
	got_any = False
	for value in s.strings():
		add_extra_chunk(ExtraChunk(lua=value))
		got_any = True

	# if not got_any:
	# 	self.error("unable to fully evaluate executed string here", args[1])

	s = self.get_type(args[5])
	got_any = False
	for value in s.strings():
		add_extra_chunk(ExtraChunk(lua=value))

	# if not got_any:
	# 	self.error("unable to fully evaluate executed string here", args[1])


def is_abstract(obj):
        return test_ancestor_flag(obj, "Abstract")


def global_lang(self, args):
        obj = self.get_type(args[0])
        return TypeTranslatedString(*obj.values)


def global_import(self, args):
        obj = self.get_type(args[0])
        if isinstance(obj, TypeString):
                for value in obj.strings():
                        if self.check_objectid(value):
                                return TypeAny()
                        else:
                                self.error("missing import", args[0])
                                self.panic()
                                return TypeAny()

        return TypeAny()



def global_get(self, args):
        obj = self.get_type(args[0])
        matches = set()

        if isinstance(obj, TypeString):
                if not obj.values:
                        return TypeMudObject()
                for value in obj.values:
                        found = self.check_objectid(value)
                        if found == True:
                                return TypeMudObject()
                        if found:
                                matches.add(TypeSpecificMudObject(found))
                        else:
                                matches.add(TypeNil())

        if not matches:
                return TypeMudObject()

        return TypeUnion(*matches)


def getter_helper(self, args, fn_name, lookup, default_value_interdeminate, default_value_dont_exist):
        key = self.get_type(args[1])
        if not isinstance(key, TypeString):
                return default_value_interdeminate

        if not key.values:
                return default_value_interdeminate

        for keyvalue in key.values:
                if keyvalue == "":
                        self.error("invalid empty key")
                        return default_value_interdeminate
                if keyvalue[0] == '!' or keyvalue[0] == '$':
                        return default_value_interdeminate

        if key.values == ["zone"]:
                return TypeZoneTag()

        obj = self.get_type(args[0])

        if isinstance(obj, TypeAny):
                return default_value_interdeminate

        matches = set()

        if type(obj.denil()) == TypeMudObject:
                # need to add a lot of keys to the schema and
                # also probably define some kind of local schema
                # system before we enable this
                #
                # we could probably do a whole-MUD analysis of
                # properties that are getted but never setted though?
                #
                # from schema import validate_key

                # for value in key.values:
                #         if not validate_key(value):
                #                 self.error(f"getting unknown key {value} on non specific object")
                #                 return TypeAny()

                return default_value_interdeminate

        specific_objects = set()

        just_any = False

        for specific in obj.types():
                if isinstance(specific, TypeString):
                        if specific.values:
                                for value in specific.values:
                                        specific_objects.add(TypeSpecificMudObject(self._universe.get(value)))
                        else:
                                just_any = True
                        continue

                if isinstance(specific, TypeSpecificMudObject):
                        specific_objects.add(specific)
                        continue

                if isinstance(specific, TypeMudObject):
                        just_any = True
                        continue

                if not isinstance(specific, TypeSpecificMudObject):
                        self.error(f"can't pass {specific} to {fn_name}")
                        just_any = True
                        continue

        if just_any:
                return default_value_interdeminate        

        for specific in specific_objects:
                if is_abstract(specific.mudobject):
                        # we're going to assume whoever clones this fills the field
                        # in.
                        matches.add(default_value_interdeminate)
                        continue
        
                for keyvalue in key.values:
                        if keyvalue not in specific.mudobject:
                                matches.add(default_value_dont_exist)
                        else:
                                matches.add(lookup(specific.mudobject[keyvalue]))

        return TypeUnion(*matches)


def global_getobj(self, args):
        def actual_lookup(result):
                if result not in self._universe:
                        return TypeNil()
                else:
                        return TypeSpecificMudObject(self._universe.get(result))

        return getter_helper(self, args, "getobj", actual_lookup, TypeMudObject(), TypeNil())


def global_getint(self, args):
        def actual_lookup(result):
                return TypeNumberRange(result)

        if len(args) > 2:
                default_value = self.get_type(args[2])
        else:
                default_value = TypeNumber()

        rval = getter_helper(self, args, "getint", actual_lookup, default_value, default_value)

        if rval is None:
                rval = default_value

        return rval


global_getintd = global_getint


def global_random(self, args):
        type = self.get_type(args[0])
        if isinstance(type, TypeNumber):
                number = type.get_single_number()
                if number is not None:
                        return TypeNumberRange(0, number-1)
        return TypeAny()

global_math_random = global_random



def global_getstr(self, args):
        def actual_lookup(result):
                return TypeString(result, tainted=False)
        
        type = self.get_type(args[1])
        values = list(type.strings())
        if values:
                tainted = False
        else:
                tainted = True

        return getter_helper(self, args, "getstr", actual_lookup, TypeString(tainted=tainted), TypeString(tainted=tainted))


def global_void(self, args):
        return TypeSpecificMudObject(self._universe.get("system_void"))
        

def global_quests(self, args):
        from universe import valid_quests
        return TypeUnion(*valid_quests.values())


def global_owner(self, args):
        obj = self.get_type(args[0])

        concrete = get_objects(obj)
        types = set()
        
        # this is technically speaking incorrect, but it's vanishingly
        # rare that an event will be valid on an object not in its
        # (snapshotted) owner.

        for obj in concrete:
                if isinstance(obj, TypeSpecificMudObject):
                        if is_abstract(obj.mudobject): # not that concrete after all!
                                return TypeMudObject()
                        owner = self._universe.get(obj.mudobject.get("owner"))
                        if owner:
                                types.add(TypeSpecificMudObject(owner))
                        else:
                                # we must be in some wilderness 
                                return TypeMudObject()
                else:
                        return TypeMudObject()

        return TypeUnion(*types)


def global_set_wanted_args(self, wanted, args):

        def is_plan(s):
                return s.startswith("plan") or s.startswith("!plan")

        was_plan = False

        # plans shouldn't be tainted
        for s in args[1].types():
                if isinstance(s, TypeStringKnownPrefix):
                        if is_plan(s.known_prefix):
                                was_plan = True
                                break

                if isinstance(s, TypeString):
                        for v in s.values:
                                if is_plan(v):
                                        was_plan = True
                                        break

        if was_plan:
                wanted[2] = TypeString(tainted=False)


def global_set(self, args):
        obj = self.get_type(args[0])
        key = self.get_type(args[1])

        def checker(obj):
                # simulations have to monkey around with their plans
                if isinstance(obj, TypeSpecificMudObject):
                        if not test_ancestor_flag(obj, "Simulation"):
                                return True
                return False
        
        if not any(checker(TypeSpecificMudObject) for obj in get_objects(obj)):
                # if it's nothing specific it's probably a clone. traps are allowed
                # to alter clones permanently.
                return

        if isinstance(key, TypeString):
                if not key.values:
                        return
                for t in type.values:
                        if t[0] != "!" and t[0] != "$":
                                self.error("attempt to set permanent property", args[1])
                                exit(1)



VERBS = {}

with open('../verbs.json') as verbs_json:
        for verb in json.load(verbs_json):
                id = verb["id"]
                minlen = verb["minlen"]
                for n in range(minlen, len(id)+1):
                        VERBS[id[0:n]] = verb
        verbs_json.close()


verb_scores = {}


def check_plan(self, obj, plan, node):

        if not obj.check_treatas_field(plan):
                self.error(f"{obj.id} missing {plan}", node)

        for specific in get_objects(obj):
                mudobject = obj.mudobject
                rantcount = mudobject.get("rant.count", 0)
                for rant in range(rantcount):
                        rant_text = mudobject.get(f"rant.{rant}")
                        if "file_plan" in rant_text:
                                self.error(f"call to file_plan even though a rant.{rant} has a file_plan", node)


def check_verb(self, obj, verb, parsed = None, node = None, is_full = False):
        if verb not in VERBS:
                self.error(f"interpret calls missing verb '{verb}'", node)

        if not verb in verb_scores:
                verb_scores[verb] = 0
        verb_scores[verb] += 1

        if not isinstance(obj, TypeSpecificMudObject):
                # we can't really do anything if its not a specific object
                # well i suppose we could see if /anything/ has it. but
                # that's really quite silly.
                return

        if verb == "file_plan":
                if parsed and len(parsed) > 1 and parsed[1][0] == '!':
                        # transient plan assumed to be set by something else
                        # on this object. XXX we could check this
                        return
                
                plan = f"plan.{parsed[1]}" if len(parsed) > 1 else "plan"
                check_plan(self, obj, plan, node)

                return

        if verb == "trap":
                # it turns out argv[1] of trap can be a trap name _or_ a parameter
                # to pass into as argv[1] of the trap! i suppose we could do a 
                # multiple phase analysis and check that the RXing trap consumes
                # this value in some way.
                if not is_full:
#                        self.warning("attempt to place parameter into a trap", node)
                        return

                mainprop = "lua.trap"
                if parsed and len(parsed) > 1:
                        specificprop = mainprop + "." + parsed[1]
                        if not obj.check_treatas_field(specificprop):
                                if obj.check_treatas_field(mainprop):
                                        # self.warning(f"specific call resolves to non-specific trap", node)
                                        pass
                                else:
                                        self.error(f"{obj.id} missing {specificprop}", node)
                return
        
        if verb == "takeoff":
                if not is_full:
                        self.warning("attempt to takeoff to a parameter!", node)
                        return
                
                if parsed and len(parsed) > 1:

                        from mudtypes import CHECK_MUDOBJECT_ID
                        if not CHECK_MUDOBJECT_ID(parsed[1]):
                                self.error("takeoff to invalid location", node)
                                return
                return

        if verb == "betold":
                tell = "tell." + parsed[1]
                luatell = "lua.tell." + parsed[1]
                if not any(key.startswith(tell) or key.startswith(luatell) for key in obj.mudobject.keys()):
                        self.warning(f"betold {parsed[1]} probably will go to telldefault", node)
                        

def get_objects_helper(obj_type):
        if isinstance(obj_type, TypeUnionType):
                for type in obj_type.types():
                        yield from get_objects(type)

        if isinstance(obj_type, TypeSpecificMudObject):
                yield obj_type

        if isinstance(obj_type, TypeString):
                for v in obj_type.values:
                        from mudtypes import CHECK_MUDOBJECT_ID
                        if found := CHECK_MUDOBJECT_ID(v):
                                yield TypeSpecificMudObject(found)

def get_objects(obj_type):
        objects = list(get_objects_helper(obj_type))
        if not objects:
                return [TypeMudObject()]
        return objects


def global_obj_file_plan(self, args):
        if len(args) < 1:
                self.error("file_plan called with insufficient arguments", self.this())

        plans = []

        if len(args) < 2:
                plans = ["plan"]
        else:
                plan_arg = self.get_type(args[1])
                for possibilities in plan_arg.strings():
                        if not possibilities.startswith("!"):
                                plans.append(f"plan.{possibilities}" if len(args) > 0 else "plan")

        obj_type = self.get_type(args[0])
        for obj in get_objects(obj_type):
                if not isinstance(obj, TypeSpecificMudObject):
                        continue
                for plan in plans:
                        check_plan(self, obj, plan, args[0])


global_obj_file_plan_with_args = global_obj_file_plan


def global_obj_interpret_wanted_args(self, wanted, args):
        # it's ok if the player taints their own command line because
        # it just gets executed with the same privs
        if args[0].is_invoker:
                wanted[1] = TypeString(tainted=True)

def global_obj_interpret(self, args):
        obj_type = self.get_type(args[0])
        cmd = self.get_type(args[1])

        if not isinstance(cmd, (TypeString, TypeAny)):
                self.error(f"bad string passed : {cmd}")
                return

        for obj in get_objects(obj_type):

                if isinstance(cmd, TypeStringKnownPrefix):
                        prefix = cmd.known_prefix
                        if " " in prefix:
                                parsed = prefix.split(" ")
                                check_verb(self, obj, parsed[0], node = args[1], is_full = False)
                        return

                for s in cmd.strings():
                        parsed = s.split(" ")
                        check_verb(self, obj, parsed[0], parsed, node = args[1], is_full = True)


def global_obj_interpretf(self, args):
        obj_type = self.get_type(args[0])
        fmt = self.get_type(args[1])
        for obj in get_objects(obj_type):
                for s in fmt.strings():
                        idx = s.index('%')
                        if idx is None:
                                continue
                        prefix = s[0:idx]
                        if " " in prefix:
                                parsed = prefix.split(" ")
                                check_verb(self, obj, parsed[0], node = args[1], is_full = False)


def global_obj_do_tell(self, args):

        mob = self.get_type(args[0])
        text = self.get_type(args[2])

        for text in text.strings():
                spellcheck(self, mob, text, args[2])

        return None


def global_obj_say(self, args):

        mob = self.get_type(args[0])
        text = self.get_type(args[1])

        for text in text.strings():
                spellcheck(self, mob, text, args[1])

        return None


def global_send(self, args):

        text = self.get_type(args[1])

        for text in text.strings():
                spellcheck(self, None, text, args[1])

        return None


def global_trap_exec(self, args):

        trap = self.get_type(args[0])

        types = []

        for val in trap.strings():
                event_type = check_valid_event(val)
                if not event_type:
                        self.error(f"call to unrecognised event {val}", args[0])
                        
                if event_type is True:
                        return
                
                passed_types = self.get_types(args)

                idx = 1

                arg_names = ["pl", "o1", "o2", "treatas", "o3", "txt", "extra"]

                orig_items = dict(event_type.items())

                event_items = [TypeString()]

                for arg in arg_names:
                        if arg_type := orig_items.get(arg):
                                event_items.append(arg_type)
                        else:
                                event_items.append(TypeNil())

                while len(event_items) < len(passed_types):
                        event_items.append(TypeNil())
                
                for passed, type, arg in zip(passed_types, event_items, args):
                        if type == TypeNil():
                                continue
                        if not type.convertible_from(passed.denil()):
                                self.error(f"can't convert {passed} to {type}", arg)
                
                types.append(event_type.return_type[0])

        if types:
                return TypeUnion(*types)
        