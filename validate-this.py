#!/usr/bin/env python3.11

import subprocess
import os
import sys
from pathlib import Path

def check_files(directory, should_pass):
    failed = False
    for file in sorted(Path(directory).glob("*")):
        if not file.is_file():
            continue
        result = subprocess.run(
            ["./validator.py", str(file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if should_pass and result.returncode != 0:
            print(f"[FAIL] {file} should have passed but failed.")
            failed = True
        elif not should_pass and result.returncode == 0:
            print(f"[FAIL] {file} should have failed but passed.")
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
