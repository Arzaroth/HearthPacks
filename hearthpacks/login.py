#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: login.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import getpass
import requests
from bs4 import BeautifulSoup

try:
    input = raw_input
except NameError:
    pass

LOGIN_FRONTPOINT = "http://www.hearthpwn.com/login"
LOGIN_ENDPOINT = "https://www.hearthpwn.com/login"
HEADERS = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0",
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class LoginError(Exception):
    """Login error exception class.
Contains the requests.Session and the last requests.Request used while trying to log in.
Raise a LoginError on failure."""
    def __init__(self, msg, session, request):
        Exception.__init__(self, msg)
        self.session = session
        self.request = request


def login(opts):
    """Logs you on HearthPwn.com, asking for credentials via stdin.
Returns a requests.Session object."""
    s = requests.Session()
    s.headers.update(HEADERS)
    if not opts['--anonymous']:
        r = s.get(LOGIN_FRONTPOINT)
        email = input('Enter your email address: ') if not "email" in opts else opts["email"]
        password = getpass.getpass('Enter your password: ') if not "password" in opts else opts["password"]
        soup = BeautifulSoup(r.content, "html.parser")
        hidden_fields = soup.find('div', class_='p-login-form').find('form').find_all('input', type='hidden')
        params = [(i['name'], i['value']) for i in hidden_fields]
        params += [('username', email)]
        params += [('loginFormPassword', password)]
        if opts['--verbose'] >= 2:
            print('Login request params:')
            print(params)
        r = s.post(LOGIN_ENDPOINT, data=params)
        if not 'User.ID' in s.cookies:
            raise LoginError('Login failed', s, r)
        if opts['--version'] >= 1:
            print('Login successful')
            print('User.ID is %s' % (s.cookies['User.ID']))
            print('Username is %s' % (s.cookies['User.Username']))
    return s
