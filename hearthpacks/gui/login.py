#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: login.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import absolute_import

import requests
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QApplication,
                             QProgressBar,
                             QLabel, QLineEdit, QPushButton, QCheckBox,
                             QVBoxLayout, QHBoxLayout, QMessageBox)
from hearthpacks import login, LoginError
from hearthpacks.gui.menu import MenuWindow, LoadingOverlay

class LoginWidget(QWidget):
    loginDone = QtCore.pyqtSignal(requests.Session)

    def __init__(self, opts, parent=None):
        QWidget.__init__(self, parent=None)
        self.opts = opts
        self.initThread()
        self.initUI()
        self.overlay = LoadingOverlay(self)
        self.overlay.hide()

    def initThread(self):
        self.loginThread = LoginThread(self.opts)
        self.loginThread.loginSuccesfull.connect(self.loginSuccesfull)
        self.loginThread.loginFailed.connect(self.loginFailed)

    def initUI(self):
        label = QLabel('HearthPwn.com Sign In', self)
        font = QtGui.QFont()
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.emailEdit = QLineEdit(self)
        self.emailEdit.setPlaceholderText("Email")
        self.emailEdit.setText(self.opts.get("email", ""))
        self.emailEdit.returnPressed.connect(self.submit)
        self.emailEdit.setFocus()

        self.passwordEdit = QLineEdit(self)
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.passwordEdit.setText(self.opts.get("password", ""))
        self.passwordEdit.setPlaceholderText("Password")
        self.passwordEdit.returnPressed.connect(self.submit)

        self.anonCheckbox = QCheckBox('Log in as anonymous', self)
        self.anonCheckbox.stateChanged.connect(self.checkboxClicked)

        self.loginButton = QPushButton('Login', self)
        self.loginButton.clicked.connect(self.submit)
        self.loginButton.setAutoDefault(True)

        loginLayout = QHBoxLayout()
        loginLayout.addStretch(1)
        loginLayout.addWidget(self.loginButton)
        loginLayout.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(label)
        vbox.addWidget(self.emailEdit)
        vbox.addWidget(self.passwordEdit)
        vbox.addWidget(self.anonCheckbox)
        vbox.addLayout(loginLayout)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def checkboxClicked(self):
        self.emailEdit.setEnabled(not self.anonCheckbox.isChecked())
        self.passwordEdit.setEnabled(not self.anonCheckbox.isChecked())

    def submit(self):
        email = self.emailEdit.text()
        password = self.passwordEdit.text()
        anonymous = self.anonCheckbox.isChecked()
        if not anonymous and not (email and password):
            QMessageBox.critical(self, "Error", "Please fill email and password fields")
        else:
            self.disable()
            self.loginThread.login(email, password, anonymous)

    def disable(self):
        self.emailEdit.setEnabled(False)
        self.passwordEdit.setEnabled(False)
        self.anonCheckbox.setEnabled(False)
        self.loginButton.setEnabled(False)
        self.overlay.show()
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def restore(self):
        self.checkboxClicked()
        self.anonCheckbox.setEnabled(True)
        self.loginButton.setEnabled(True)
        self.overlay.hide()
        QApplication.restoreOverrideCursor()

    def loginSuccesfull(self, session):
        self.restore()
        self.loginDone.emit(session)

    def loginFailed(self, error):
        self.restore()
        QMessageBox.critical(self, "Error", str(error))

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


class LoginWindow(MenuWindow):
    def __init__(self, opts):
        MenuWindow.__init__(self)
        self.login = LoginWidget(opts, self)
        self.setCentralWidget(self.login)


class LoginThread(QtCore.QThread):
    loginSuccesfull = QtCore.pyqtSignal(requests.Session)
    loginFailed = QtCore.pyqtSignal(LoginError)

    def __init__(self, opts):
        QtCore.QThread.__init__(self)
        self.mutex = QtCore.QMutex()
        self.opts = opts

    def login(self, email, password, anonymous):
        locker = QtCore.QMutexLocker(self.mutex)
        self.email = email
        self.password = password
        self.anonymous = anonymous
        if not self.isRunning():
            self.start()

    def run(self):
        try:
            self.mutex.lock()
            opts = dict(self.opts, **{
                'email': self.email,
                'password': self.password,
                '--anonymous': self.anonymous,
            })
            self.mutex.unlock()
            session = login(opts)
            self.loginSuccesfull.emit(session)
        except LoginError as e:
            self.loginFailed.emit(e)
