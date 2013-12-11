#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import logging

# TODO Add type dict or list and way to del with name or id

class Db(object):
    "Manage simple database in json file"

    def __init__(self, db_name='default', dry_run=False, db_type='dict', db_file='./%s.json' % __name__, logger=__name__):
        "type can be dict|list"
        self._db_file = db_file
        self._db_type = db_type
        self._db_name = db_name
        self._dry_run = dry_run
        self._logger = logging.getLogger(logger)
        self._db = {}

    def __enter__(self):
        self._load_db()
        return self

    def __exit__(self, type, value, traceback):
        if not self._dry_run:
            self._dump_db()

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
        except IOError, e:
            self._logger.critical("%s - Dump db IOError: %s Can't write datas"
                                    % (__name__, e))

    def save(self, key, value=None):
        "Write data in the database"
        if self._db_type == 'list':
            self._db[self._db_name].append(key)
        else:
            self._db[self._db_name][key] = value

    def remove(self, key):
        "Write data in the database"
        if self._db_type == 'list':
            self._db[self._db_name].pop(key)
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
            return self._db.get(self._db_name, {}).get(key, None)

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
