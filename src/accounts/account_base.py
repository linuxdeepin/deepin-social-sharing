#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Deepin Technology Co., Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer

class TimeoutThread(QThread):
    timeout = pyqtSignal()

    def __init__(self, timeout=10*1000):
        super(TimeoutThread, self).__init__()
        self._timer = QTimer()
        self._timer.setSingleShot(False)
        self._timer.setInterval(timeout)
        self._timer.timeout.connect(self._timeout)

        self.started.connect(lambda: self._timer.start())
        self.finished.connect(lambda: self._timer.stop())

    def _timeout(self):
        self.quit()
        self.timeout.emit()

class AccountBase(QObject):
    """Base class all the SNS accounts should inherit"""
    succeeded = pyqtSignal(str, arguments=["accountType"])
    failed = pyqtSignal(str, int, arguments=["accountType", "reason"])

    loginFailed = pyqtSignal(str, arguments=["accountType"])
    getAuthorizeUrlFailed = pyqtSignal(str, arguments=["accountType"])

    authorizeUrlGot = pyqtSignal(str, str,
        arguments=["accountType", "authorizeUrl"])
    accountInfoGot = pyqtSignal(str, "QVariant",
        arguments=["accountType", "accountInfo"])

    def __init__(self):
        super(AccountBase, self).__init__()
        self.enabled = False
        self._getAuthorizeUrlThread = None
        self._getAccountInfoThread = None

    def valid(self):
        raise NotImplementedError()

    def share(self, text, pic):
        raise NotImplementedError()

    def getAuthorizeUrl(self):
        raise NotImplementedError()

    def cancelGetAuthorizeUrl(self):
        raise NotImplementedError()

    def getVerifierFromUrl(self, url):
        raise NotImplementedError()

    def getAccountInfoWithVerifier(self, verifier):
        raise NotImplementedError()

    def generateTag(self, text):
        raise NotImplementedError()