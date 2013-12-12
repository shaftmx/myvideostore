#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import logging
import os
from shutil import copy2 as copy
from os.path import join
import hashlib

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

def check_file_consistency(source, dest, dry_run=False):
    if dry_run:
         LOG.warning('Check file consistency between %s -> %s' % (source, dest))
    else:
        LOG.info('Check file consistency between %s -> %s' % (source, dest))
        sum_source = hashlib.md5(open(source, 'rb').read()).hexdigest()
        sum_dest = hashlib.md5(open(dest, 'rb').read()).hexdigest()
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


