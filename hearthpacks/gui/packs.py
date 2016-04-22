#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: packs.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import absolute_import

import shutil
import tempfile
try:
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtCore import pyqtSignal, pyqtSlot
    from PyQt5.QtWidgets import (QWidget, QAction, QSizePolicy,
                                 QHBoxLayout, QVBoxLayout, QGridLayout,
                                 QLabel, QLineEdit, QPushButton,
                                 QSpinBox, QComboBox, QMessageBox)
except ImportError:
    try:
        from PySide import QtCore, QtGui
        from PySide.QtCore import Signal as pyqtSignal
        from PySide.QtCore import Slot as pyqtSlot
        from PySide.QtGui import (QWidget, QAction, QSizePolicy,
                                  QHBoxLayout, QVBoxLayout, QGridLayout,
                                  QLabel, QLineEdit, QPushButton,
                                  QSpinBox, QComboBox, QMessageBox)
    except ImportError:
        raise SystemExit("PyQt5 and PySide not found. Unable to launch GUI.")

from hearthpacks import PackOpener, PackError
from hearthpacks.packs import Pack, Card
from hearthpacks.packs import PACKS_TYPE
from hearthpacks.gui.menu import MenuWindow, LoadingOverlay

class PackOpenerWidget(QWidget):
    def __init__(self, opts, session, parent=None):
        QWidget.__init__(self, parent)
        self.opts = opts
        self.session = session
        self.count = 0
        self.initThread()
        self.initUI()

    def initThread(self):
        self.packOpenerThread = PackOpenerThread()
        self.packOpenerThread.submitted.connect(self.pack_submitted)
        self.packOpenerThread.opened.connect(self.pack_opened)
        self.packOpenerThread.failed.connect(self.pack_failed)
        self.packOpenerThread.done.connect(self.stop)
        self.imageLoaderPool = ImageLoaderTaskerPool()
        self.imageLoaderPool.done.connect(self.images_loaded)

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
        for pack_type in PACKS_TYPE:
            self.packTypeCombobox.addItem(pack_type)
        self.packTypeCombobox.setCurrentIndex(PACKS_TYPE.index(self.opts['PACK_TYPE']))
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

        self.midLabel = QLabel("No packs submitted yet", self)
        self.cardLabels = []
        cardGroup = QHBoxLayout()
        cardGroup.setAlignment(QtCore.Qt.AlignCenter)
        for i in range(5):
            self.cardLabels.append(QLabel(parent=self))
            self.cardLabels[-1].hide()
            self.cardLabels[-1].setScaledContents(True)
            self.cardLabels[-1].setAlignment(QtCore.Qt.AlignCenter)
            self.cardLabels[-1].setMinimumSize(1, 1)
            self.cardLabels[-1].installEventFilter(self)
            cardGroup.addWidget(self.cardLabels[-1])

        midScreen = QGridLayout()
        midScreen.addWidget(self.midLabel, 0, 0, alignment=QtCore.Qt.AlignCenter)
        midScreen.addLayout(cardGroup, 1, 0, alignment=QtCore.Qt.AlignCenter)

        counterTextLabel = QLabel('Pack count:', self)
        self.counterLabel = QLabel('0', self)
        counterGroup = QHBoxLayout()
        counterGroup.setAlignment(QtCore.Qt.AlignLeft)
        counterGroup.setSpacing(1)
        counterGroup.addWidget(counterTextLabel)
        counterGroup.addWidget(self.counterLabel)

        packScoreTextLabel = QLabel('Pack score:', self)
        self.packScoreLabel = QLabel('-', self)
        packScoreGroup = QHBoxLayout()
        packScoreGroup.setAlignment(QtCore.Qt.AlignRight)
        packScoreGroup.setSpacing(1)
        packScoreGroup.addWidget(packScoreTextLabel)
        packScoreGroup.addWidget(self.packScoreLabel)

        botScreen = QGridLayout()
        botScreen.addLayout(counterGroup, 0, 0, alignment=QtCore.Qt.AlignLeft)
        botScreen.addLayout(packScoreGroup, 0, 1, alignment=QtCore.Qt.AlignRight)

        grid = QGridLayout()
        grid.addLayout(topScreen, 0, 0, alignment=QtCore.Qt.AlignTop)
        grid.addLayout(midScreen, 1, 0, alignment=QtCore.Qt.AlignCenter)
        grid.addLayout(botScreen, 2, 0, alignment=QtCore.Qt.AlignBottom)
        self.setLayout(grid)

    @pyqtSlot()
    def go(self):
        self.goButton.hide()
        self.stopButton.show()
        self.attemptsSpin.setEnabled(False)
        self.highThresholdSpin.setEnabled(False)
        self.lowThresholdSpin.setEnabled(False)
        self.packTypeCombobox.setEnabled(False)
        self.count = 0
        opts = dict(self.opts, **{
            '--attempts': self.attemptsSpin.value(),
            '--threshold': self.highThresholdSpin.value(),
            '--low-threshold': self.lowThresholdSpin.value(),
            'PACK_TYPE': self.packTypeCombobox.currentText(),
        })
        self.packOpenerThread.open_packs(PackOpener(opts, self.session))

    @pyqtSlot()
    def stop(self):
        self.stopButton.hide()
        self.goButton.show()
        self.attemptsSpin.setEnabled(True)
        self.highThresholdSpin.setEnabled(True)
        self.lowThresholdSpin.setEnabled(True)
        self.packTypeCombobox.setEnabled(True)
        self.packOpenerThread.stop()

    @pyqtSlot()
    def pack_opened(self):
        self.count += 1
        self.counterLabel.setText(str(self.count))

    @pyqtSlot(Pack)
    def pack_submitted(self, pack):
        self.packScoreLabel.setText(str(pack.score))
        self.imageLoaderPool.get_images(pack)

    @pyqtSlot(PackError)
    def pack_failed(self, error):
        self.stop()
        QMessageBox.critical(self, "Error", str(error))

    @pyqtSlot(list)
    def images_loaded(self, result):
        self.midLabel.setText("Last submitted pack:")
        for (card, filename), label in zip(result, self.cardLabels):
            label.card = card
            if card.golden:
                res = QtGui.QMovie(filename)
                label.card_data = res
                label.setMovie(res)
                res.start()
            else:
                res = QtGui.QPixmap(filename)
                label.card_data = res
                label.setPixmap(res)
            label.show()

    def eventFilter(self, source, event):
        if (source in self.cardLabels and event.type() == QtCore.QEvent.Resize):
            if source.card.golden:
                source.card_data.setScaledSize(source.size())
            else:
                source.setPixmap(source.card_data.scaled(source.size(),
                                                         QtCore.Qt.KeepAspectRatio,
                                                         QtCore.Qt.SmoothTransformation))
        return QWidget.eventFilter(self, source, event)

class PackOpenerWindow(MenuWindow):
    logout = pyqtSignal()

    def __init__(self, opts, session):
        MenuWindow.__init__(self)
        opts['--score'] = -1
        self.packOpener = PackOpenerWidget(opts, session, self)
        self.setCentralWidget(self.packOpener)

    def initUI(self):
        MenuWindow.initUI(self)
        self.setFixedSize(1400, 550)

    def initMenus(self):
        logoutAction = QAction('&Logout', self)
        logoutAction.setShortcut('Ctrl+L')
        logoutAction.setStatusTip('Back to login screen')
        logoutAction.triggered.connect(self.propagate_logout)
        self.fileMenu.addAction(logoutAction)
        self.fileMenu.addSeparator()
        MenuWindow.initMenus(self)

    @pyqtSlot()
    def propagate_logout(self):
        self.logout.emit()


class PackOpenerThread(QtCore.QThread):
    opened = pyqtSignal()
    submitted = pyqtSignal(Pack)
    failed = pyqtSignal(PackError)
    done = pyqtSignal()

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.mutex = QtCore.QMutex()
        self.pack_opener = None
        self._isRunning = False

    def open_packs(self, pack_opener):
        locker = QtCore.QMutexLocker(self.mutex)
        self._isRunning = True
        self.pack_opener = pack_opener
        if not self.isRunning():
            self.start()

    def stop(self):
        self._isRunning = False

    def run(self):
        if not self.pack_opener:
            return
        try:
            for i in range(self.pack_opener.opts['--attempts']):
                if not self._isRunning:
                    break
                self.mutex.lock()
                pack = self.pack_opener.open_pack()
                self.mutex.unlock()
                self.opened.emit()
                if pack.submitted:
                    self.submitted.emit(pack)
                self.sleep(self.pack_opener.opts['--wait'])
        except PackError as e:
            self.failed.emit(e)
        finally:
            self.mutex.unlock()
            self.done.emit()


class ImageLoaderSignals(QtCore.QObject):
    done = pyqtSignal(Card, object)


class ImageLoaderWorker(QtCore.QRunnable):
    def __init__(self, card):
        QtCore.QRunnable.__init__(self)
        self.card = card
        self.signals = ImageLoaderSignals()

    def run(self):
        data = self.card.image_data
        if data:
            self.signals.done.emit(self.card, data)


class ImageLoaderTaskerPool(QtCore.QObject):
    done = pyqtSignal(list)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(5)
        self.cards = []
        self.result = {}
        self.tmpdir = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.tmpdir)

    @pyqtSlot(Card, object)
    def add_result(self, card, data):
        with tempfile.NamedTemporaryFile(dir=self.tmpdir, delete=False) as f:
            f.write(data)
        self.result[card] = f.name
        done_cards = [i for i in self.cards if all(x in self.result.keys() for x in i)]
        self.cards = [i for i in self.cards if not all(x in self.result.keys() for x in i)]
        for done in done_cards:
            self.done.emit([(x, self.result[x]) for x in done])

    def get_images(self, pack):
        self.cards.append(pack.cards)
        for card in pack.cards:
            if card in self.result.keys():
                self.add_result(card, self.result[card])
            else:
                worker = ImageLoaderWorker(card)
                worker.signals.done.connect(self.add_result)
                self.pool.start(worker)
