#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: menu.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import absolute_import

from PyQt5.QtWidgets import QMainWindow, QAction, qApp

class MenuWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        self.statusBar()
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(exitAction)
        self.setGeometry(300, 300, 300, 250)
