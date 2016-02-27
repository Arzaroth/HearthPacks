#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: hearthpacks.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import sys
import json
import time
from docopt import docopt
from schema import Schema, And, Or, Use, Optional, SchemaError
from setup import VERSION
from hearthpacks import login, LoginError
from hearthpacks import open_packs, save_pack, PackError
from hearthpacks import Gui

PRGM = "HearthPacks"

INTRO = """
{prgm} {ver}
Spam pack opening of HearthPwn.com to get the best score possible.
""".format(prgm=PRGM, ver='.'.join(VERSION))

AUTHOR = """Original program by Arzaroth <lekva@arzaroth.com>."""

__doc__ = """
{intro}

Usage:
  {prgm} [-ngc FILE] [-v | -vv] [--attempts=<number>] [--score=<number>] [--threshold=<number>] [--low-threshold=<number>] [--wait=<seconds>]
  {prgm} -h
  {prgm} --version

Options:
  -n, --anonymous                               Open and save packs as anonymous.
  -g, --gui                                     Open in GUI mode.
  -c <file>, --config=<file>                    Path to configuration file, see Notes.
  -a <number>, --attempts=<number>              Number of attemps to get the best pack [default: 1000].
  -s <number>, --score=<number>                 Minimum score to consider pack [default: 25000].
  -t <number>, --threshold=<number>             Score needed to auto-submit good pack [default: 50000].
  -l <number>, --low-threshold=<number>         Score needed to auto-submit bad pack [default: 60].
  -w <seconds>, --wait=<seconds>                Number of seconds between to packs opening [default: 2].
  -v, --verbose                                 Print more text.
  -V, --version                                 Show version number.
  -h, --help                                    Show this help and exit.

Notes:
  The configuration file is a json file containing HearthPwn.com credential and all possible options.
  The file can contain any option specified here, plus two extra keys, "email" and "password".
  Configuration file take over command line arguments.
  You can look at the examples provided with the source code.

Disclaimer:
  I am not affiliated in any way to HearthPwn.com.
  This is an automatization tool, no more.

Author:
  {author}
""".format(intro=INTRO, author=AUTHOR, prgm=PRGM)

if __name__ == '__main__':
    opts = docopt(__doc__, version='.'.join(VERSION))
    schema = Schema({
        Optional('--config'): Or(None, Use(open), error="--config must be a readable file"),
        Optional('--attempts'): And(Use(int), lambda n: n > 0, error='--attempts must be a strictly positive integer'),
        Optional('--score'): And(Use(int), lambda n: n >= 0, error='--score must be a positive integer'),
        Optional('--threshold'): And(Use(int), lambda n: n >= 0, error='--threshold must be a positive integer'),
        Optional('--low-threshold'): And(Use(int), lambda n: n > 0, error='--low-threshold must be a strictly positive integer'),
        Optional('--verbose'): And(Use(int), lambda n: 0 <= n <= 2, error='--verbose must be specified at most twice'),
        Optional('--wait'): And(Use(int), lambda n: n >= 0, error='--wait must be a positive integer'),
        object: object,
    })
    try:
        opts = schema.validate(opts)
        if opts['--config']:
            config = json.loads(opts['--config'].read())
            opts.update(config)
    except (SchemaError, json.decoder.JSONDecodeError) as e:
        print('Error: %s' % (str(e)), file=sys.stderr)
    else:
        if opts['--gui']:
            sys.exit(Gui(opts).run())
        try:
            session = login(opts)
            pack = open_packs(opts, session)
            print('The best pack is:')
            print(pack)
            save_pack(opts, pack, session, "Best pack")
        except LoginError as e:
            print(e, file=sys.stderr)
        except PackError as e:
            print(e, file=sys.stderr)
            if e.pack and e.pack.score:
                print('Waiting 10 secs to submit...')
                time.sleep(10)
                print('Save best pack before error:')
                print(e.pack)
                save_pack(opts, e.pack, session, "Best pack")
    sys.exit(0)
