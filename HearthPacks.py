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

INTRO = """HearthPacks.py {ver}
Spam pack opening of HearthPwn.com to get the best score possible.
""".format(ver='.'.join(VERSION))

AUTHOR = """Original program by Arzaroth <lekva@arzaroth.com>."""

__doc__ = """{intro}
Usage:
  HearthPacks.py [-ngc FILE] [-v | -vv] [--attempts NUMBER] [--score NUMBER]
                 [--threshold NUMBER] [--low-threshold NUMBER]
                 [--wait SECONDS] [PACK_TYPE]
  HearthPacks.py -h
  HearthPacks.py --version

Arguments:
  PACK_TYPE                             Type of packs to be opened,
                                        case insensitive, see Notes.

Options:
  -n, --anonymous                       Open and save packs as anonymous.
  -g, --gui                             Open in GUI mode.
  -c FILE, --config=FILE                Path to configuration file, see Notes.
  -a NUMBER, --attempts=NUMBER          Number of attemps to get the best pack
                                        [default: 1000].
  -s NUMBER, --score=NUMBER             Minimum score to consider pack
                                        [default: 25000].
  -t NUMBER, --threshold=NUMBER         Score needed to auto-submit good pack
                                        [default: 50000].
  -l NUMBER, --low-threshold=NUMBER     Score needed to auto-submit bad pack
                                        [default: 60].
  -w SECONDS, --wait=SECONDS            Number of seconds between two packs
                                        opening [default: 2].
  -v, --verbose                         Print more text.
  -V, --version                         Show version number.
  -h, --help                            Show this help and exit.

Notes:
  There are currently two pack types supported, wild and tgt.
  If PACK_TYPE is not supplied, it will be wild packs.
  This might change in the future as more types are added to HearthPwn.com.

  The configuration file is a json file containing HearthPwn.com credential
  and all possible options.
  The file can contain any option specified here, plus two extra keys,
  "email" and "password".
  Configuration file take over command line arguments.
  You can look at the examples provided with the source code.

Disclaimer:
  I am not affiliated in any way to HearthPwn.com.
  This is an automatization tool, no more.

Author:
  {author}
""".format(intro=INTRO, author=AUTHOR)

def parse_args():
    opts = docopt(__doc__, version='.'.join(VERSION))
    schema = Schema({
        Optional('PACK_TYPE'):
        Or(None, lambda s: s.lower() in ["wild", "tgt"],
           error="PACK_TYPE should be wild or tgt"),
        Optional('--config'):
        Or(None, Use(open),
           error="--config must be a readable file"),
        Optional('--attempts'):
        And(Use(int), lambda n: n > 0,
            error='--attempts must be a strictly positive integer'),
        Optional('--score'):
        And(Use(int), lambda n: n >= 0,
            error='--score must be a positive integer'),
        Optional('--threshold'):
        And(Use(int), lambda n: n >= 0,
            error='--threshold must be a positive integer'),
        Optional('--low-threshold'):
        And(Use(int), lambda n: n > 0,
            error='--low-threshold must be a strictly positive integer'),
        Optional('--wait'):
        And(Use(int), lambda n: n >= 0,
            error='--wait must be a positive integer'),
        object: object,
    })
    opts = schema.validate(opts)
    opts['PACK_TYPE'] = opts['PACK_TYPE'].lower() if opts['PACK_TYPE'] else "wild"
    if opts['--config']:
        config = json.loads(opts['--config'].read())
        opts.update(config)
    return opts

if __name__ == '__main__':
    try:
        opts = parse_args()
    except (SchemaError, json.decoder.JSONDecodeError) as e:
        print('Error: %s' % (str(e)), file=sys.stderr)
        sys.exit(1)
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
            sys.exit(2)
        except PackError as e:
            print(e, file=sys.stderr)
            if e.pack and e.pack.score:
                print('Waiting 10 secs to submit...')
                time.sleep(10)
                print('Save best pack before error:')
                print(e.pack)
                save_pack(opts, e.pack, session, "Best pack")
    sys.exit(0)
