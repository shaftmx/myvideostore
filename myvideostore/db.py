#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import logging

# TODO delete dict behavior. List is enough

class Db(object):
    "Manage simple database in json file"

    def __init__(self, db_type='default', db_file='./%s.json' % __name__, logger=__name__):
        self._db_file = db_file
        self._db_type = db_type
        self._db = {db_type: {}}
        self._logger = logging.getLogger(logger)

    def __enter__(self):
        self._load_db()
        return self

    def __exit__(self, type, value, traceback):
        self._dump_db()

    def _load_db(self):
        "Load the database from file"
        try:
            with open(self._db_file, 'r') as f:
                self._db = json.load(f)
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

    def save(self, key, value):
        "Write data in the database"
        self._db[self._db_type][key] = value

    def get(self, key):
        "Get data from database"
        return self._db.get(self._db_type, {}).get(key, None)

    def get_all(self):
        "Get all data from database"
        return self._db.get(self._db_type, {})

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
