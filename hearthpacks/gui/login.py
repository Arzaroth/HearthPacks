#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: login.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import absolute_import

import requests
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QSizePolicy, QApplication,
                             QProgressBar,
                             QLabel, QLineEdit, QPushButton, QCheckBox,
                             QVBoxLayout, QHBoxLayout, QMessageBox)
from hearthpacks import login, LoginError
from hearthpacks.gui.menu import MenuWindow

class LoginWidget(QWidget):
    loginDone = QtCore.pyqtSignal(requests.Session)

    def __init__(self, opts, parent):
        QWidget.__init__(self, parent)
        self.opts = opts
        self.initThread()
        self.initUI()

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

        loginButton = QPushButton('LoginButton', self)
        loginButton.clicked.connect(self.submit)
        loginButton.setAutoDefault(True)

        loginLayout = QHBoxLayout()
        loginLayout.addStretch(1)
        loginLayout.addWidget(loginButton)
        loginLayout.addStretch(1)

        self.loadingBar = QProgressBar()
        self.loadingBar.setRange(0, 0)
        self.loadingBar.hide()

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(label)
        vbox.addWidget(self.emailEdit)
        vbox.addWidget(self.passwordEdit)
        vbox.addWidget(self.anonCheckbox)
        vbox.addLayout(loginLayout)
        vbox.addWidget(self.loadingBar)
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
        self.loadingBar()
        self.setEnabled(False)
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def restore(self):
        self.loadingBar.show()
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def loginSuccesfull(self, session):
        self.restore()
        self.loginDone.emit(session)

    def loginFailed(self, error):
        self.restore()
        QMessageBox.critical(self, "Error", str(error))


class LoginWindow(MenuWindow):
    def __init__(self, opts):
        MenuWindow.__init__(self)
        self.setWindowTitle("Login")
        self.login = LoginWidget(opts, self)
        self.setCentralWidget(self.login)


class LoginThread(QtCore.QThread):
    loginSuccesfull = QtCore.pyqtSignal(requests.Session)
    loginFailed = QtCore.pyqtSignal(LoginError)

    def __init__(self, opts):
        QtCore.QThread.__init__(self)
        self.opts = opts

    def login(self, email, password, anonymous):
        self.email = email
        self.password = password
        self.anonymous = anonymous
        self.start()

    def run(self):
        try:
            session = login(dict(self.opts, **{
                'email': self.email,
                'password': self.password,
                '--anonymous': self.anonymous,
            }))
            self.loginSuccesfull.emit(session)
        except LoginError as e:
            self.loginFailed.emit(e)
