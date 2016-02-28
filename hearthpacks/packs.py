#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: packs.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

from __future__ import print_function, absolute_import, unicode_literals

import sys
import time
import requests
from bs4 import BeautifulSoup
from hearthpacks.utils import InterruptedHandlerGenerator

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
    def __init__(self, msg, pack=None):
        Exception.__init__(self, msg)
        self.pack = pack


class Card(object):
    def __init__(self, li):
        self.card_id = int(li['data-id'])
        self.golden = "is-gold" in li.attrs['class']
        href = li.find('a', class_='card-front')['href']
        self.name = href.replace('/cards/%d-' % (self.card_id), '').replace('-', ' ')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s%s" % (self.name, " (Golden)" if self.golden else "")


class Pack(object):
    def __init__(self, request=None):
        self.request = request
        if request:
            self.soup = BeautifulSoup(request.content, "html.parser")
            self.score = int(self.soup.find('span', class_='pack-score')['data-score'])
            cards_tag = self.soup.find('ul', class_='pack-results').find_all('li')
            self._cards = (Card(li) for li in cards_tag)
        else:
            self.soup = BeautifulSoup("", "html.parser")
            self.score = 0
            self._cards = ()

    @property
    def cards(self):
        self._cards = list(self._cards)
        return self._cards

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Score: %s\nCards: %s" % (self.score, ", ".join(map(str, self.cards)))


def submit_threshold(opts, pack, session, i):
    if pack.score >= opts['--threshold']:
        print('Pack has reached the threshold, pack is:')
        print(pack)
        save_pack(opts, pack, session, "Threshold %d" % (i))

def submit_low(opts, pack, session, i):
    if pack.score <= opts['--low-threshold']:
        print('Pack is below low threshold, is:')
        print(pack)
        save_pack(opts, pack, session, "Low Threshold %d" % (i))

def open_packs(opts, session):
    """Open packs from HearthPwn.com using request.Session object retrieved from login.
Returns the requests.Request object with the best pack.
Raise a PackError if no pack is good enough."""
    best_pack = Pack()
    for i in InterruptedHandlerGenerator(range(1, opts['--attempts'] + 1)):
        try:
            r = session.get(PACKS_FRONTPOINT[opts['PACK_TYPE']], timeout=5)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            r = None
        pack = Pack(r)
        if pack.score == 0:
            raise PackError("Unable to acquire pack", best_pack)
        if opts['--verbose'] >= 1:
            print('Pack #%d opened, score is: %d' % (i, pack.score))
        if (opts['--score'] and
            pack.score > best_pack.score and
            pack.score > opts['--score']):
            submit_threshold(opts, best_pack, session, i)
            best_pack = pack
            if opts['--verbose'] >= 1:
                print('New best pack found!')
                print(best_pack)
        else:
            submit_threshold(opts, pack, session, i)
            submit_low(opts, pack, session, i)
        time.sleep(opts['--wait'])
    if best_pack.score == 0:
        raise PackError('No pack was good enough')
    return best_pack

def save_pack(opts, pack, session, title=None):
    """Save pack to HearthPwn.com using request.Session object retrieved from login.
Returns the request.Request object of the saved pack."""
    hidden_fields = (pack.soup.find('form', class_='pack-save-form')
                     .find_all('input', type='hidden'))
    params = [(i['name'], i['value']) for i in hidden_fields]
    title_tag = (pack.soup.find('form', class_='pack-save-form')
                 .find('input', id='field-title'))
    if not title:
        title = input('Enter a title for the pack: ')
    params += [(title_tag['name'], title)]
    if opts['--verbose'] >= 2:
        print('Save pack request params:')
        print(params)
    try:
        r = session.post(PACKS_ENDPOINT, data=params, timeout=5,
                         headers={'Referer': PACKS_FRONTPOINT[opts['PACK_TYPE']]})
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise PackError("Unable to submit pack")
    if r:
        print('Save pack url: %s' % (r.url))
    else:
        print('Pack could not be saved', file=sys.stderr)
    return r
