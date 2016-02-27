#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: utils.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import absolute_import

import signal

class InterruptedHandlerGenerator(object):
    def __init__(self, iterable, sig=signal.SIGINT):
        self.iterable = iter(iterable)
        self.sig = sig

    def __iter__(self):
        self.interrupted = False
        self.released = False
        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.interrupted:
            raise StopIteration()
        try:
            return next(self.iterable)
        except StopIteration as e:
            self.release()
            raise e

    def release(self):
        if self.released:
            return False
        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True
