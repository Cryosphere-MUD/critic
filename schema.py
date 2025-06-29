#!/usr/bin/env python3.11

import json, pprint, luapatt

known_props = []
pattern_props = []

with open('../schema.json') as schema_json:
        schema = json.load(schema_json)
        schema_json.close()

        for package, part in schema.items():
                props = part.get("properties")
                if not props:
                        continue

                for key, data in props.items():
                        if "%" in key:
                                pattern_props.append("^" + key + "$")
                        else:
                                known_props.append(key)
                        


def validate_key(key):
        if key in known_props:
                return True

        for pattern in pattern_props:
                if luapatt.find(source=key, pattern=pattern):
                        print(key, pattern)
                        return True

        if key[0] == '!':
                return True

        if key[0] == '$':
                return True

        return False