#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: packs.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import absolute_import

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QGridLayout,
                             QLabel, QLineEdit, QPushButton)
from hearthpacks import PackOpener, PackError
from hearthpacks.gui.menu import MenuWindow

class PackOpenerWidget(QWidget):
    def __init__(self, opts, session, parent=None):
        QWidget.__init__(self, parent)
        self.opts = opts
        self.session = session
        self.initThread()
        self.initUI()

    def initThread(self):
        pass

    def initUI(self):
        pass


class PackOpenerWindow(MenuWindow):
    def __init__(self, opts, session):
        MenuWindow.__init__(self)
        self.packOpener = PackOpenerWidget(opts, session, self)
        self.setCentralWidget(self.packOpener)


class PackOpenerThread(QtCore.QThread):
    def __init__(self, opts, session):
        QtCore.QThread.__init__(self)
        self.opts = opts
        self.session = session

    def run(self):
        pass
