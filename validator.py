#!/usr/bin/env python3.11

import sys, typing, argparse
import glob
from errors import had_error, set_no_warnings
from luatypes import TypeAny
from universe import UNIVERSE_BY_ID, TREATAS_USERS
from worldchecker import check_world
from chunkvalidate import validate_chunk

CHUNKS = []

parser = argparse.ArgumentParser()
parser.add_argument("--spellcheck", help="Enable spellchecking mode", action="store_true")
parser.add_argument("--world", help="Only validate the world, no verbs", action="store_true")
parser.add_argument("--unknown", help="Errors for unknown events", action="store_true")
parser.add_argument("--no-warnings", help="Disable warnings", action="store_true")
parser.add_argument("--resolution-only", help="Only do symbol resolution", action="store_true")
parser.add_argument("objects", nargs="*", help="Objects or a file to test")

args = parser.parse_args()

if args.no_warnings:
        set_no_warnings(True)

import spellcheck
if args.spellcheck:
        spellcheck.enable()
else:
        spellcheck.disable()

ZONE = []

for arg in args.objects:
        try:
                file = open(arg, "r")
                CHUNKS.append(file.read())
        except:
                ZONE.append(arg)

if CHUNKS:
        for chunk in CHUNKS:
                validate_chunk(chunk, return_type=[TypeAny()])
        if had_error():
                print("there were errors")
                exit(1)
        else:
                print("all ok")
                exit(0)

check_world(UNIVERSE_BY_ID, args, ZONE)

#        for file in glob.glob(TMP_PREFIX + "*lua*"):
#                process_file(file)

print("Finished validating")

#from functions import verb_scores
#sorted_verb_scores = sorted(verb_scores.items(), key=lambda a: a[1], reverse=True)
#print(sorted_verb_scores)

if had_error():
        exit(1)
