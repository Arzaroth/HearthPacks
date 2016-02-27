#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: login.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import absolute_import

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QWidget, QSizePolicy,
                             QLabel, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QMessageBox)
from hearthpacks import login, LoginError
from hearthpacks.gui.menu import MenuWindow

class LoginWidget(QWidget):
    def __init__(self, opts, parent):
        QWidget.__init__(self, parent)
        self.opts = opts
        self.session = None
        self.initUI()

    def initUI(self):
        label = QLabel('HearthPwn.com Sign In')
        font = QtGui.QFont()
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.email = QLineEdit(self)
        self.email.setPlaceholderText("Email")
        self.email.setText(self.opts.get("email", ""))
        self.email.setFocus()

        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.email.setText(self.opts.get("password", ""))
        self.password.setPlaceholderText("Password")
        self.password.returnPressed.connect(self.submit)

        login = QPushButton('Login', self)
        login.clicked.connect(self.submit)
        login.setAutoDefault(True)

        loginLayout = QHBoxLayout()
        loginLayout.addStretch(1)
        loginLayout.addWidget(login)
        loginLayout.addStretch(1)

        grid = QGridLayout()
        grid.setSpacing(5)
        grid.setRowStretch(0, 1)
        grid.addWidget(label, 1, 1)
        grid.addWidget(self.email, 2, 1)
        grid.addWidget(self.password, 3, 1)
        grid.addLayout(loginLayout, 4, 1)
        grid.setRowStretch(5, 1)

        self.setLayout(grid)

    def submit(self):
        email = self.email.text()
        password = self.password.text()
        if not (email and password):
            QMessageBox.critical(self, "Error", "Please fill email and password fields")
        else:
            try:
                self.session = login(dict(**self.opts, email=email, password=password))
            except LoginError as e:
                QMessageBox.critical(self, "Error", str(e))


class LoginWindow(MenuWindow):
    def __init__(self, opts):
        MenuWindow.__init__(self)
        self.setWindowTitle("Login")
        self.login = LoginWidget(opts, self)
        self.setCentralWidget(self.login)
