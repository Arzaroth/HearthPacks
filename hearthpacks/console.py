#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: console.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import print_function, absolute_import

import sys
import time
from retry import retry
from hearthpacks import login, LoginError
from hearthpacks import PackOpener, PackError
from hearthpacks.utils import InterruptedHandlerGenerator

class Console(object):
    def __init__(self, opts):
        self.opts = opts

    def run(self):
        ret = 0
        try:
            session = login(self.opts)
            pack_opener = PackOpener(self.opts, session)
            for i in InterruptedHandlerGenerator(range(self.opts['--attempts'])):
                pack_opener.open_pack()
                time.sleep(self.opts['--wait'])
            if self.opts['--version'] >= 1:
                print('The best pack is:')
                print(pack_opener.best_pack)
            if pack_opener.best_pack.score > 0:
                pack_opener.save_pack("Best pack")
        except LoginError as e:
            print(e, file=sys.stderr)
            ret = 2
        except PackError as e:
            print(e, file=sys.stderr)
            ret = 3
            if pack_opener.best_pack.score > 0:
                if self.opts['--verbose'] >= 1:
                    print("Trying to submit best pack before error:")
                    print(e.pack)
                @retry(PackError, tries=5, delay=2)
                def save_pack():
                    pack_opener.save_pack("Best pack")
        return ret
