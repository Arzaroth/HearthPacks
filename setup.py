#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: setup.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#


from __future__ import print_function, absolute_import

import os
from setuptools import setup, find_packages

VERSION = ("v3", "0", "1")

if __name__ == '__main__':
    setup(
        name='HearthPacks',
        version='.'.join(VERSION),
        license='BSD',

        # url='',
        # download_url='%s.zip' % ('.'.join(VERSION)),

        author='Marc-Etienne Barrut',
        author_email='lekva@arzaroth.com',

        description='A simple tool to spam pack opening on HearthPwn.com',
        long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
        keywords='hearthpwn packs open spam',

        packages=find_packages('.'),
        scripts=['HearthPacks.py'],

        install_requires=open('requirements.txt').read().split('\n'),
    )
