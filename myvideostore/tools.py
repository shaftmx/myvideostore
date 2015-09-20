#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Author: Gaël Lambert (gaelL) <gael.lambert@netwiki.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
from shutil import copy2 as copy
from os.path import join
import hashlib
from functools import partial

LOG = logging.getLogger(__name__)

class Print(object):
    @staticmethod
    def white(texte):
        print "\033[37m%s\033[0m" % texte

    @staticmethod
    def grey(texte):
        print "\033[30m%s\033[0m" % texte
     
    @staticmethod
    def grey_strong(texte):
        print "\033[1;30m%s\033[0m" % texte
     
    @staticmethod
    def blue(texte):
        print "\033[34m%s\033[0m" % texte
     
    @staticmethod
    def red(texte):
        print "\033[31m%s\033[0m" % texte
     
    @staticmethod
    def green(texte):
        print "\033[32m%s\033[0m" % texte
     
    @staticmethod
    def pink(texte):
        print "\033[35m%s\033[0m" % texte
     
    @staticmethod
    def yellow(texte):
        print "\033[33m%s\033[0m" % texte
     
    @staticmethod
    def cyan(texte):
        print "\033[36m%s\033[0m" % texte

def copy_file(source, dest, dry_run=False):
    if dry_run:
        LOG.warning('Copy file : %s' % dest)
    else:
        LOG.info('Copy file : %s' % dest)
        copy(source, dest)

# To optimize speed bug less secure, we can change bufsize to read only 100Mo max
# For each files
def md5(filename, chunksize=2**15, bufsize=-1):
    m = hashlib.md5()
    with open(filename, 'rb', bufsize) as f:
        for chunk in iter(partial(f.read, chunksize), b''):
            m.update(chunk)
    return m.hexdigest()

def check_file_consistency(source, dest, dry_run=False):
    if dry_run:
         LOG.warning('Check file consistency between %s -> %s' % (source, dest))
         return True
    else:
        LOG.info('Check file consistency between %s -> %s' % (source, dest))
        sum_source = md5(filename=source)
        sum_dest = md5(filename=dest)
        LOG.debug('Sum : %s %s' % (sum_source, sum_dest))
        if sum_source != sum_dest: return False
        else: return True

def create_dir(path, dry_run=False):
    if dry_run:
        LOG.warning('Create directory : %s' % path)
    else:
        if not os.path.isdir(path):
            LOG.info('Create directory : %s' % path)
            os.makedirs(path)
    
def remove_empty_dir(path, dry_run=False):
    for root, dirs, files in os.walk(path,topdown=False):
        for name in dirs:
            fname = os.path.join(root,name)
            # Check if dir exist because removedirs recursively remove dir
            if not os.path.isdir(fname): continue
            if not os.listdir(fname):
                if not dry_run:
                    os.removedirs(fname)
                LOG.info('Delete empty directory : %s' % fname)

def len_without_none(array):
    len = 0
    for i in array:
        if i is None: continue
        len += 1
    return len

class Keycode(object):
    # int to key chr(10) Inverse str -> int ord('\n')
    # LOG.critical('Key : %s' % c)
    code_return = 127
    code_del = 126
    code_enter = 10
    code_up = 65
    code_down = 66
    code_left = 68
    code_right = 67
    code_q = 113
    code_space = 32
    code_h = 104
    code_v = 118

