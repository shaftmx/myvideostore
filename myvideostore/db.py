#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Author: Gaël Lambert <gael.lambert@netwiki.fr>
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

import json
import logging
import os
from myvideostore.tools import copy_file, check_file_consistency

# TODO Add type dict or list and way to del with name or id

class Db(object):
    "Manage simple database in json file"

    def __init__(self, db_name='default', dry_run=False, db_type='dict',
                 db_file='./%s.json' % __name__, logger=__name__,
                 safe_dump=False):
        "type can be dict|list"
        self._safe_dump = safe_dump
        self._db_file = db_file
        self._db_type = db_type
        self._db_name = db_name
        self._dry_run = dry_run
        self._logger = logging.getLogger(logger)
        if self._db_type == 'list':
            self._db = {self._db_name: []}
        else:
            self._db = {self._db_name: {}}

    def __enter__(self):
        self._load_db()
        if self._safe_dump and os.path.isfile(self._db_file): # Backup database
            self._logger.info('Safe mode, backup db %s' % '%s.orig' % self._db_file)
            copy_file(source=self._db_file, dest='%s.orig' % self._db_file,
                      dry_run=self._dry_run)
            if not check_file_consistency(source=self._db_file,
                                          dest='%s.orig' % self._db_file,
                                          dry_run=self._dry_run):
                raise Exception('Unable to do safe load. Copy %s' % self._db_file)
        return self

    def __exit__(self, type, value, traceback):
        if not self._dry_run:
            dump_db_success = self._dump_db()
            if self._safe_dump and os.path.isfile('%s.orig' % self._db_file):
                # If all things gone ok, remove the backup
                if dump_db_success:
                    self._logger.info('Write Db ok, remove backup')
                    os.remove('%s.orig' % self._db_file)
                else:
                    self._logger.critical('Write Db error, keep backup in place')


    def _load_db(self):
        "Load the database from file"
        try:
            with open(self._db_file, 'r') as f:
                self._db = json.load(f)
                # Add our db_name if not existe (in case of multi type db)
                if not self._db_name in self._db:
                    if self._db_type == 'list':
                        self._db.update({self._db_name: []})
                    else:
                        self._db.update({self._db_name: {}})
        except IOError, e:
            self._logger.warning('%s - Load db IOError: %s Use new default db %s'
                                    % (__name__, e, self._db))

    def _dump_db(self):
        "Dump data in json database file"
        try:
            with open(self._db_file, 'w') as f:
                json.dump(self._db, f)
            return True
        except IOError, e:
            self._logger.critical("%s - Dump db IOError: %s Can't write datas"
                                    % (__name__, e))
            return False

    def save(self, key, value=None):
        "Write data in the database"
        if self._db_type == 'list':
            self._db[self._db_name].append(key)
        else:
            self._db[self._db_name][key] = value

    def remove(self, key):
        "Write data in the database"
        if self._db_type == 'list':
            try:
                self._db[self._db_name].pop(key)
            except IndexError:
                self._logger.critical("Unable to find id %s" % key)
                
        else:
            del self._db[self._db_name][key]

    def flush_all(self):
        "Flush all datas in the database"
        if self._db_type == 'list':
            self._db[self._db_name] = []
        else:
            self._db[self._db_name] = {}

    def get(self, key):
        "Get data from database"
        if self._db_type == 'list':
            return key if myItem in self._db[self._db_name] else None
        else:
            return self._db.get(self._db_name, {}).get('%s' % key.decode('utf-8'), None)

    def get_all(self):
        "Get all data from database"
        if self._db_type == 'list':
            return self._db.get(self._db_name, [])
        else:
            return self._db.get(self._db_name, {})

#    def consume(self):
#        while self._db:
#            yield self._db.pop()

# DB base va simplement faire les dump et autre choses génériques.
# Implementer 2 autre db dessus pour retourner les données qu'on veut


## La db va contenir le path et un hash du fihier et status (copied
#{
#    '/bla' : 'unused',
#    '/foo' : 'unused',
#}
#
## La db va contenir le status (vue ou non) et les nouvelles videos
#
#{
#    'path' : 'unused'
#}
#{
#    'New video': 'unused'
#}
