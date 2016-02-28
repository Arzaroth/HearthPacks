#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: menu.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import absolute_import, division

import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QPalette, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QWidget

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


class LoadingOverlay(QWidget):
    def __init__(self, parent=None, interval=50):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.counter = 0
        self.interval = interval

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.NoPen))

        for i in range(6):
            if int(self.counter / 10) % 6 == i:
                factor = self.counter % 10
                if factor >= 5:
                    factor = 5 - (self.counter % 5)
                painter.setBrush(QBrush(QColor(95 + factor * 32, 127, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width() / 2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height() / 2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)

        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(self.interval)
        self.counter = 0

    def hideEvent(self, event):
        self.killTimer(self.timer)

    def timerEvent(self, event):
        self.counter += 1
        self.update()
