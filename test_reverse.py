#!/usr/bin/env python3

# to run this script :
# $ nosetest3
# or
# $ python3 test_reverse.py

import os
import sys
from time import time
from contextlib import redirect_stdout
from nose.tools import assert_equal
from pathlib import Path
from io import StringIO

from reverse import reverse
from lib.context import Context

TESTS = Path('tests')

SYMBOLS = {
        TESTS / 'server.bin': ["main", "connection_handler"],
        TESTS / 'pendu.bin': ["_main", "___main", "__imp___cexit"],
        TESTS / 'shellcode.bin': ["0x0"],
        TESTS / 'malloc.bin': ["malloc"],
        TESTS / 'entryloop1.bin': ["0x4041b0"],
        }

OPTIONS = {
    TESTS / 'shellcode.bin': ["--raw x86"],
    TESTS / 'malloc.bin': ["--raw x64", "--rawbase 0x77110"],
    TESTS / 'entryloop1.bin': ["--raw x64", "--rawbase 0x4041b0"],
    }


def test_reverse():
    for p in TESTS.glob('*.bin'):
        for symbol in sorted(SYMBOLS.get(p, [None])):
            yield reverse_file, str(p), symbol, OPTIONS.get(p, [])

def reverse_file(filename, symbol, options):
    ctx = Context()
    ctx.sectionsname = False
    ctx.color = False
    ctx.filename = filename
    ctx.entry = symbol
    ctx.quiet = True

    for o in options:
        if o == "--raw x86":
            ctx.raw_type = "x86"
        elif o == "--raw x64":
            ctx.raw_type = "x64"
        elif o.startswith("--rawbase"):
            ctx.raw_base = int(o.split(" ")[1], 16)

    sio = StringIO()
    with redirect_stdout(sio):
        reverse(ctx)
    postfix = '{0}.rev'.format('' if symbol is None else '_' + symbol)
    with open(filename.replace('.bin', postfix)) as f:
        assert_equal(sio.getvalue(), f.read())


def color(text, c):
    return "\x1b[38;5;" + str(c) + "m" + text + "\x1b[0m"


if __name__ == "__main__":
    start = time()
    passed = 0
    nb = 0
    failed = []

    for reverse_file, path, symbol, options in test_reverse():
        name = os.path.basename(path)

        nb += 1

        try:
            reverse_file(path, symbol, options)
            print(".", end="")
            passed += 1
        except AssertionError:
            print(color("F", 1), end="")
            failed.append(name)
        except:
            print(color("E", 1), end="")
            failed.append(name)

        sys.stdout.flush()

    elapsed = time()
    elapsed = elapsed - start
    print("\n%d/%d tests passed successfully in %fs" % (passed, nb, elapsed))

    for p in failed:
        print("failed:", p)
