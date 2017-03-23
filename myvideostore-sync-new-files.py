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
from myvideostore.tools import Print
from myvideostore.db import Db
from myvideostore.tools import create_dir, copy_file, remove_empty_dir, check_file_consistency
import argparse
from os.path import join
import os
import re
import sys
import subprocess

# Init logging level with debug stream handler
LOG = logging.getLogger()
LOG.setLevel(logging.CRITICAL)
LOG.setLevel(logging.INFO)

# Get args
PARSER = argparse.ArgumentParser()
PARSER.add_argument("-d", "--dry-run",
            help="Launch script in dry run mode",
            action='store_true',
            default=False)
PARSER.add_argument("-l", "--list-exclude",
            help="List all excludes with ID. (Don't copy any file)",
            action='store_true',
            default=False)
PARSER.add_argument("-a", "--add-exclude",
            help="Add exclude in exclude list (Don't copy any file)",
            metavar='exclude',
            type=str,
            nargs='+')
PARSER.add_argument("-x", "--del-exclude",
            help="Delete all exclude specified (Don't copy any file)",
            metavar='exclude_id',
            type=int,
            nargs='+')
PARSER.add_argument("-L", "--list-include",
            help="List all includes with ID. (Don't copy any file)",
            action='store_true',
            default=False)
PARSER.add_argument("-A", "--add-include",
            help=("Add include in include list. "
                  "Is take before an exclude (Don't copy any file)"),
            metavar='include',
            type=str,
            nargs='+')
PARSER.add_argument("-X", "--del-include",
            help="Delete all include specified (Don't copy any file)",
            metavar='include_id',
            type=int,
            nargs='+')
PARSER.add_argument("-s", "--source",
            help="Source directory to get videos",
            type=str,
            required=True)
PARSER.add_argument("-t", "--target",
            help="Target directory where you want copy your videos",
            type=str,
            required=True)
PARSER.add_argument("--pre",
            help="Launch a command before sync directory",
            metavar='pre_cmd',
            type=str)
PARSER.add_argument("--post",
            help="Launch a command after sync directory",
            metavar='post_cmd',
            type=str)
PARSER.add_argument("--db-list",
            help="List all file already copied in db",
            action='store_true',
            default=False)
PARSER.add_argument("--db-purge",
            help=("Specify a regex and purge matching entry in db"),
            metavar='regex',
            type=str)
ARGS = PARSER.parse_args()

DRY_RUN = ARGS.dry_run

if DRY_RUN: logformat = '%(asctime)s %(levelname)s / DRY_RUN! -: %(message)s'
else: logformat =  '%(asctime)s %(levelname)s -: %(message)s'
# Set logger formater
formatter = logging.Formatter(logformat)
hdl = logging.StreamHandler(); hdl.setFormatter(formatter); LOG.addHandler(hdl)

def run_cmd(cmd, dry_run=False):
    if dry_run:
        LOG.warning('Exec command %s' % cmd)
    else:
        LOG.info('Exec command %s' % cmd)
        output = subprocess.call(cmd, shell=True)
        if output != 0:
            LOG.critical('Command ERROR %s return code : %d' % (cmd, output))
            sys.exit(output)

def sync_dir():
    "Sync source dir with dest dir"
    LOG.warning('Start sync dir ...')
    # Launch database connection
    with Db(db_name='sync',
            db_file='%s/db.json' % ARGS.target,
            dry_run=DRY_RUN,
            safe_dump=True) as db:
        # For each files
        for dir_path, dirs, files in os.walk(ARGS.source):
            if not files: continue
            # For each files in dir
            for file_name in files:
                # Filter db file and windobe file ...
                if file_name in ['db.json', 'db.json.orig', 'Thumbs.db']:
                    continue
                # Exemple : -s Video/foo -t dest
                # Give : src = Video/foo : relative = foo : dst = dest/foo
                dir_source      = dir_path
                dir_relative    = re.sub(r'%s/?' % ARGS.source,'', dir_source)
                dir_dest        = join(ARGS.target, dir_relative)
                file_source     = join(dir_source, file_name)
                file_relative   = join(dir_relative, file_name)
                file_dest       = join(dir_dest, file_name)
    
                if db.get(file_relative) is None:
                    if is_include(file_relative) \
                    or not is_exclude(file_relative):
                        create_dir(dir_dest, dry_run=DRY_RUN)
                        try:
                            copy_file(file_source, file_dest, dry_run=DRY_RUN)
                        except IOError as error:
                            LOG.critical("Error can't copy file %s : %s"
                                         % (file_dest, error))
                        if check_file_consistency(file_source, file_dest, dry_run=DRY_RUN):
                            db.save(file_relative, 'unused')
                        else:
                            LOG.critical("Error file is not consistent "
                                         "the sum don't match")
        # Clean empty dir after sync
        remove_empty_dir(ARGS.target, dry_run=DRY_RUN)

def add_exclude():
    "Add an exclude dir filter"
    # Launch database connection
    with Db(db_name='exclude', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        for exclude in ARGS.add_exclude:
            db.save(exclude)

def del_exclude():
    "Del an exclude"
    # Launch database connection
    with Db(db_name='exclude', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        for exclude_id in ARGS.del_exclude:
            db.remove(exclude_id)

def list_exclude():
    "List all excludes"
    # Launch database connection
    with Db(db_name='exclude', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        print 'Excludes :'
        for key, exclude in enumerate(db.get_all()):
            print '  - %s : "%s"' % (key, exclude)

def is_exclude(line):
    "Check if file match exclude"
    with Db(db_name='exclude', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        for exclude in db.get_all():
            if re.search(exclude, line):
                return True
        return False

def add_include():
    "Add an include dir filter"
    # Launch database connection
    with Db(db_name='include', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        for include in ARGS.add_include:
            db.save(include)

def del_include():
    "Del an include"
    # Launch database connection
    with Db(db_name='include', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        for include_id in ARGS.del_include:
            db.remove(include_id)

def is_include(line):
    "Check if file match include"
    with Db(db_name='include', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        for include in db.get_all():
            if re.search(include, line):
                return True
        return False

def list_include():
    "List all includes"
    # Launch database connection
    with Db(db_name='include', db_type='list', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        print 'Includes :'
        for key, include in enumerate(db.get_all()):
            print '  - %s : "%s"' % (key, include)

def db_list():
    "List all file in db"
    with Db(db_name='sync', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        for k,v in db.get_all().iteritems():
            print " - %s" % k.encode('utf-8')

def db_purge(regex):
    "Purge file matching regex in db"
    _buffer = []
    with Db(db_name='sync', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
        print "File in db matching %s :" % regex
        for k,v in db.get_all().iteritems():
            name = k.encode('utf-8')
            matched = re.match(regex, name)
            if matched is not None:
                _buffer.append(name)
                print " - %s" % (name)
    
        choice = raw_input('Realy want to delete there files y/N:')
        if choice == 'y':
            for name in _buffer:
                db.remove(name)


if __name__ == "__main__":

    # Create target dir
    create_dir(ARGS.target, dry_run=DRY_RUN)
    # List exclude
    if ARGS.list_exclude:
        list_exclude()
    # List include
    elif ARGS.list_include:
        list_include()
    # Add exclude
    elif ARGS.add_exclude:
        add_exclude()
    # Del exclude
    elif ARGS.del_exclude:
        del_exclude()
    # Add include
    elif ARGS.add_include:
        add_include()
    # Del include
    elif ARGS.del_include:
        del_include()
    # db_list
    elif ARGS.db_list:
        db_list()
    # db_purge
    elif ARGS.db_purge:
        db_purge(ARGS.db_purge)
    # Sync
    else:
        # Launch pre command
        if ARGS.pre:
            run_cmd(ARGS.pre,dry_run=DRY_RUN)
        # Sync dir
        sync_dir()
        # Launch post command
        if ARGS.post:
            run_cmd(ARGS.post,dry_run=DRY_RUN)

