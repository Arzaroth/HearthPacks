#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import absolute_import

import signal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from hearthpacks.gui.login import LoginWindow
from hearthpacks.gui.packs import PackOpenerWindow

class Gui(QApplication):
    def __init__(self, opts):
        QApplication.__init__(self, [])
        self.opts = opts
        self.initUI()

    def initUI(self):
        self.loginWindow = LoginWindow(self.opts)
        self.loginWindow.loginDone.connect(self.loginDone)
        self.loginWindow.show()

    def reinitUI(self):
        self.packWindow.hide()
        self.loginWindow.show()

    def loginDone(self, session):
        self.loginWindow.hide()
        self.packWindow = PackOpenerWindow(self.opts, session)
        self.packWindow.logout.connect(self.reinitUI)
        self.packWindow.show()

    def run(self):
        return self.exec_()
