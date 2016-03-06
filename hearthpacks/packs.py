#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: packs.py
# by Arzaroth Lekva
# lekva@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import sys
import requests
from bs4 import BeautifulSoup

try:
    input = raw_input
except NameError:
    pass

PACKS_FRONTPOINT = {
    'wild': "http://www.hearthpwn.com/packs/simulator/1-hearthpwn-wild-pack",
    'tgt': "http://www.hearthpwn.com/packs/simulator/2-hearthstone-tgt",
}
PACKS_ENDPOINT = "http://www.hearthpwn.com/packs/save"

class PackError(Exception):
    """Pack error exception class."""
    pass


class Card(object):
    def __init__(self, li):
        self.card_id = int(li['data-id'])
        self.golden = "is-gold" in li.attrs['class']
        href = li.find('a', class_='card-front')['href']
        self.name = href.replace('/cards/%d-' % (self.card_id), '').replace('-', ' ')
        if self.golden:
            src = li.find('video')
            self.img_src = src['data-gifurl']
        else:
            src = li.find('img')
            self.img_src = src['src']
        self.width = int(src['width'])
        self.height = int(src['height'])
        self._image_data = None

    @property
    def image_data(self):
        if not self._image_data:
            try:
                self._image_data = requests.get(self.img_src).content
            except requests.ConnectionError:
                pass
        return self._image_data

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s%s" % (self.name, " (Golden)" if self.golden else "")


class Pack(object):
    def __init__(self, request=None):
        self.request = request
        self.submitted = False
        if request:
            self.soup = BeautifulSoup(request.content, "html.parser")
            self.score = int(self.soup.find('span', class_='pack-score')['data-score'])
            cards_tag = self.soup.find('ul', class_='pack-results').find_all('li')
            self.cards = [Card(li) for li in cards_tag]
        else:
            self.soup = BeautifulSoup("", "html.parser")
            self.score = 0
            self._cards = ()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Score: %s\nCards: %s" % (self.score, ", ".join(map(str, self.cards)))


class PackOpener(object):
    def __init__(self, opts, session):
        self.opts = opts
        self.session = session
        self.best_pack = Pack()
        self.counter = 0

    def submit_threshold(self, pack):
        if pack.score >= self.opts['--threshold']:
            if self.opts['--verbose'] >= 1:
                print('Pack has reached the threshold, pack is:')
                print(pack)
            self.save_pack("Threshold", pack)

    def submit_low(self, pack):
        if pack.score <= self.opts['--low-threshold']:
            if self.opts['--verbose'] >= 1:
                print('Pack is below low threshold, is:')
                print(pack)
            self.save_pack("Low Threshold", pack)

    def open_pack(self):
        """Open a pack from HearthPwn.com using request.Session object retrieved from login.
Raise a PackError if the pack could not be retrieved.
Returns the Pack object of the opened pack."""
        try:
            r = self.session.get(PACKS_FRONTPOINT[self.opts['PACK_TYPE']], timeout=5)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            r = None
        pack = Pack(r)
        if pack.score == 0:
            raise PackError("Unable to acquire pack")
        self.counter += 1
        if self.opts['--verbose'] >= 1:
            print('Pack #%d opened, score is: %d' % (self.counter, pack.score))
        if (self.opts['--score'] != -1 and
            pack.score > self.best_pack.score and
            pack.score > self.opts['--score']):
            self.submit_threshold(self.best_pack)
            self.best_pack = pack
            if self.opts['--verbose'] >= 1:
                print('New best pack found!')
                print(self.best_pack)
        else:
            self.submit_threshold(pack)
            self.submit_low(pack)
        return pack

    def save_pack(self, title=None, pack=None):
        """Save pack to HearthPwn.com using request.Session object retrieved from login.
If no pack is provided, use current best pack.
Raise PackError if the pack is invalid or could not be saved.
Returns the request.Request object of the saved pack."""
        pack = pack or self.best_pack
        if pack.score == 0:
            raise PackError("Invalid pack")
        hidden_fields = (pack.soup.find('form', class_='pack-save-form')
                         .find_all('input', type='hidden'))
        params = [(i['name'], i['value']) for i in hidden_fields]
        title_tag = (pack.soup.find('form', class_='pack-save-form')
                     .find('input', id='field-title'))
        if not title:
            title = input('Enter a title for the pack: ')
        params += [(title_tag['name'], title)]
        if self.opts['--verbose'] >= 2:
            print('Save pack request params:')
            print(params)
        try:
            r = self.session.post(PACKS_ENDPOINT, data=params, timeout=5,
                                  headers={'Referer': PACKS_FRONTPOINT[self.opts['PACK_TYPE']]})
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise PackError("Unable to submit pack")
        if r:
            pack.submitted = True
            if self.opts['--verbose'] >= 1:
                print('Save pack url: %s' % (r.url))
        else:
            if self.opts['--verbose'] >= 1:
                print('Pack could not be saved', file=sys.stderr)
        return r
