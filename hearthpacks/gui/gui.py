#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import absolute_import

import signal
from PyQt5.QtWidgets import QApplication
from hearthpacks.gui.login import LoginWindow

class Gui(QApplication):
    def __init__(self, opts):
        QApplication.__init__(self, [])
        self.opts = opts
        self.window = LoginWindow(opts)
        self.window.show()

    def run(self):
        return self.exec_()
