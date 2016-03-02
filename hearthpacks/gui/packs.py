#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: packs.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import absolute_import

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QAction,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton,
                             QSpinBox, QComboBox)
from hearthpacks import PackOpener, PackError
from hearthpacks.gui.menu import MenuWindow

class PackOpenerWidget(QWidget):
    def __init__(self, opts, session, parent=None):
        QWidget.__init__(self, parent)
        self.opts = opts
        self.pack_opener = PackOpener(opts, session)
        self.initThread()
        self.initUI()

    def initThread(self):
        pass

    def initUI(self):
        attemptsLabel = QLabel('Attempts', self)
        self.attemptsSpin = QSpinBox(self)
        self.attemptsSpin.setRange(1, 1000000)
        self.attemptsSpin.setValue(self.opts['--attempts'])
        attemptsGroup = QHBoxLayout()
        attemptsGroup.setAlignment(QtCore.Qt.AlignCenter)
        attemptsGroup.setSpacing(5)
        attemptsGroup.addWidget(attemptsLabel)
        attemptsGroup.addWidget(self.attemptsSpin)

        highThresholdLabel = QLabel('High threshold', self)
        self.highThresholdSpin = QSpinBox(self)
        self.highThresholdSpin.setRange(0, 10000000)
        self.highThresholdSpin.setValue(self.opts['--threshold'])
        highThresholdGroup = QHBoxLayout()
        highThresholdGroup.setAlignment(QtCore.Qt.AlignCenter)
        highThresholdGroup.setSpacing(5)
        highThresholdGroup.addWidget(highThresholdLabel)
        highThresholdGroup.addWidget(self.highThresholdSpin)

        lowThresholdLabel = QLabel('Low threshold', self)
        self.lowThresholdSpin = QSpinBox(self)
        self.lowThresholdSpin.setRange(1, 10000000)
        self.lowThresholdSpin.setValue(self.opts['--low-threshold'])
        lowThresholdGroup = QHBoxLayout()
        lowThresholdGroup.setAlignment(QtCore.Qt.AlignCenter)
        lowThresholdGroup.setSpacing(5)
        lowThresholdGroup.addWidget(lowThresholdLabel)
        lowThresholdGroup.addWidget(self.lowThresholdSpin)

        packTypeLabel = QLabel('Pack type', self)
        self.packTypeCombobox = QComboBox(self)
        self.packTypeCombobox.addItem("wild")
        self.packTypeCombobox.addItem("tgt")
        self.packTypeCombobox.setCurrentIndex(["wild", "tgt"].index(self.opts['PACK_TYPE']))
        packTypeGroup = QHBoxLayout()
        packTypeGroup.setAlignment(QtCore.Qt.AlignCenter)
        packTypeGroup.setSpacing(5)
        packTypeGroup.addWidget(packTypeLabel)
        packTypeGroup.addWidget(self.packTypeCombobox)

        self.goButton = QPushButton('Go!', self)
        self.goButton.clicked.connect(self.go)
        self.goButton.setAutoDefault(True)
        self.goButton.setFixedWidth(50)
        self.stopButton = QPushButton('Stop', self)
        self.stopButton.clicked.connect(self.stop)
        self.stopButton.setAutoDefault(True)
        self.stopButton.setFixedWidth(50)
        self.stopButton.hide()

        topScreen = QHBoxLayout()
        topScreen.setSpacing(20)
        topScreen.addLayout(attemptsGroup)
        topScreen.addLayout(highThresholdGroup)
        topScreen.addLayout(lowThresholdGroup)
        topScreen.addLayout(packTypeGroup)
        topScreen.addWidget(self.goButton)
        topScreen.addWidget(self.stopButton)

        vbox = QVBoxLayout()
        vbox.addLayout(topScreen)
        vbox.setAlignment(topScreen, QtCore.Qt.AlignTop)

        self.setLayout(vbox)

    def go(self):
        self.goButton.hide()
        self.stopButton.show()

    def stop(self):
        self.stopButton.hide()
        self.goButton.show()


class PackOpenerWindow(MenuWindow):
    logout = QtCore.pyqtSignal()

    def __init__(self, opts, session):
        MenuWindow.__init__(self)
        opts['--score'] = -1
        self.packOpener = PackOpenerWidget(opts, session, self)
        self.setCentralWidget(self.packOpener)

    def initUI(self):
        MenuWindow.initUI(self)
        self.setFixedSize(960, 400)

    def initMenus(self):
        logoutAction = QAction('&Logout', self)
        logoutAction.setShortcut('Ctrl+L')
        logoutAction.setStatusTip('Back to login screen')
        logoutAction.triggered.connect(self.logout.emit)
        self.fileMenu.addAction(logoutAction)
        self.fileMenu.addSeparator()
        MenuWindow.initMenus(self)


class PackOpenerThread(QtCore.QThread):
    def __init__(self, opts, pack_opener):
        QtCore.QThread.__init__(self)
        self.opts = opts
        self.pack_opener = pack_opener

    def run(self):
        pass


class ImageLoaderWorker(QtCore.QRunnable):
    done = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self):
        pass

    def run(self):
        pass
