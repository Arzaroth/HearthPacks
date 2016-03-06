#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: gui.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import absolute_import

import requests
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import pyqtSlot
except ImportError:
    try:
        from PySide.QtGui import QApplication
        from PySide.QtCore import Slot as pyqtSlot
    except ImportError:
        raise SystemExit("PyQt5 and PySide not found. Unable to launch GUI.")

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

    @pyqtSlot()
    def reinitUI(self):
        self.packWindow.hide()
        self.loginWindow.show()

    @pyqtSlot(requests.Session)
    def loginDone(self, session):
        self.loginWindow.hide()
        self.packWindow = PackOpenerWindow(self.opts, session)
        self.packWindow.logout.connect(self.reinitUI)
        self.packWindow.show()

    def run(self):
        return self.exec_()
