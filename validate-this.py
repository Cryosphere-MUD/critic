#!/usr/bin/env python3.11

import subprocess
import os
import sys

from errors import set_quiet, clear_error, had_error
from luatypes import TypeAny
from pathlib import Path
from chunkvalidate import validate_chunk

def check_files(directory, should_pass):
    failed = False
    for file in sorted(Path(directory).glob("*")):
        if not file.is_file():
            continue

        opened = open(file, "r")
        chunk = opened.read()

        file_success = False

        clear_error()
        set_quiet(True)

        try:
                validate_chunk(chunk, return_type=[TypeAny()])
                if had_error():
                        file_success = False
                else:
                        file_success = True
        except:
                # import traceback
                # traceback.print_exc()
                # print("exception")
                file_success = False

        if file_success != should_pass:
                print(file, "should_pass", should_pass, "success", file_success)
                failed = True

    return failed

def main():
    any_failed = False
    any_failed |= check_files("tests/valid", should_pass=True)
    any_failed |= check_files("tests/failing", should_pass=False)

    if any_failed:
        print("Some tests failed.")
        sys.exit(1)
    else:
        print("All tests passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
