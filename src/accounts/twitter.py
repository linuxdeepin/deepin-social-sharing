#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Deepin Technology Co., Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

from _sdks.twitter_sdk import UserClient, TwitterAuthError

from account_base import AccountBase, TimeoutThread
from utils import getUrlQuery
from constants import TWITTER, ShareFailedReason

from PyQt5.QtCore import pyqtSignal

APP_KEY = 'r2HHabDu8LDQCELxk2cA'
APP_SECRET = '9e4LsNOvxWVWeEgC5gthL9Q78F7FDsnT7lUIBruyQmI'
CALLBACK_URL = 'http://www.linuxdeepin.com'

class GetAuthorizeUrlThread(TimeoutThread):
    getAuthorizeUrlFailed = pyqtSignal()
    authorizeUrlGot = pyqtSignal(str, arguments=["authorizeUrl"])

    def __init__(self, client=None):
        super(GetAuthorizeUrlThread, self).__init__()
        self._client = client
        self.timeout.connect(self.getAuthorizeUrlFailed)

    def setClient(self, client):
        self._client = client

    def run(self):
        try:
            token = self._client.get_authorize_token()
            self.authorizeUrlGot.emit(token["auth_url"])
        except Exception:
            self.getAuthorizeUrlFailed.emit()

class GetAccountInfoThread(TimeoutThread):
    getAccountInfoFailed = pyqtSignal()
    accountInfoGot = pyqtSignal("QVariant", arguments=["accountInfo"])

    def __init__(self, client=None, verifier=None):
        super(GetAccountInfoThread, self).__init__()
        self._client = client
        self._verifier = verifier
        self.timeout.connect(self.getAccountInfoFailed)

    def setClient(self, client):
        self._client = client

    def setVerifier(self, verifier):
        self._verifier = verifier

    def run(self):
        try:
            token_info = self._client.get_access_token(self._verifier)
            info = [token_info["user_id"], token_info["screen_name"],
                    token_info["oauth_token"], token_info["oauth_token_secret"]]
            self.accountInfoGot.emit(info)
        except Exception:
            self.getAccountInfoFailed.emit()

class Twitter(AccountBase):
    def __init__(self, uid='', username='',
                 access_token='', access_token_secret=''):
        super(Twitter, self).__init__()
        self.uid = uid
        self.username = username

        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._client = UserClient(APP_KEY,
                                  APP_SECRET,
                                  access_token,
                                  access_token_secret)

        self._getAuthorizeUrlThread = GetAuthorizeUrlThread(self._client)
        self._getAuthorizeUrlThread.authorizeUrlGot.connect(
            lambda x: self.authorizeUrlGot.emit(TWITTER, x))
        self._getAuthorizeUrlThread.getAuthorizeUrlFailed.connect(
            lambda: self.getAuthorizeUrlFailed.emit(TWITTER))

        self._getAccountInfoThread = GetAccountInfoThread(self._client)
        self._getAccountInfoThread.accountInfoGot.connect(
            self.handleAccountInfoGot)
        self._getAccountInfoThread.getAccountInfoFailed.connect(
            lambda: self.loginFailed.emit(TWITTER))

    def handleAccountInfoGot(self, info):
        self.accountInfoGot.emit(TWITTER, info)
        self.uid = info[0]
        self.username = info[1]

    def valid(self):
        # self._client.access_token and self._client.access_token are not
        # reliable here, they are set to request_token and request_token_secret
        # after the request getting request token.
        return bool(self.uid and self.username)

    def share(self, text, pic=None):
        if not self.enabled: return

        try:
            if pic:
                with open(pic, "rb") as _pic:
                    self._client.api.statuses.update_with_media.post(status=text,
                                                                     media=_pic)
            else:
                self._client.api.statuses.update.post(status=text)
            self.succeeded.emit(TWITTER)
        except Exception, e:
            if e.__class__ == TwitterAuthError:
                self.failed.emit(TWITTER, ShareFailedReason.Authorization)
            else:
                self.failed.emit(TWITTER, ShareFailedReason.Other)

    def getAuthorizeUrl(self):
        self._client = UserClient(APP_KEY, APP_SECRET)
        self._getAuthorizeUrlThread.setClient(self._client)
        self._getAuthorizeUrlThread.start()

    def cancelGetAuthorizeUrl(self):
        if self._getAuthorizeUrlThread.isRunning():
            self._getAuthorizeUrlThread.terminate()

    def getVerifierFromUrl(self, url):
        query = getUrlQuery(url)
        return query.get("oauth_verifier")

    def getAccountInfoWithVerifier(self, verifier):
        self._getAccountInfoThread.setClient(self._client)
        self._getAccountInfoThread.setVerifier(verifier)
        self._getAccountInfoThread.start()

    def generateTag(self, text):
        return "#%s " % text