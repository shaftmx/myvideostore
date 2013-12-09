#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from myvideostore.tools import Print
from myvideostore.db import Db
from myvideostore.tools import create_dir, remove_empty_dir
import argparse
import os
import re


# TODO
#X  * Prendre en arg un dossier src et un dst
#  * Faire un fichier db à la racine de ce dossier dst
#  * La db va contenir le path et un hash du fihier et status (copied)
#  * Possible d'ajouter des excludes pour les dossiers.
#  * copier les nouveaux fichiers et reconstruire l'arbo
#  * Apres passage du sync clean des dossiers vides
#  * + Ajouter la liste des nouvelles videos dans la db du videostore


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
PARSER.add_argument("-s", "--source",
            help="Source directory to get videos",
            type=str,
            required=True)
PARSER.add_argument("-t", "--target",
            help="Target directory where you want copy your videos",
            type=str,
            required=True)
ARGS = PARSER.parse_args()

DRY_RUN = ARGS.dry_run

if DRY_RUN: logformat = '%(asctime)s %(levelname)s / DRY_RUN! -: %(message)s'
else: logformat =  '%(asctime)s %(levelname)s -: %(message)s'
# Set logger formater
formatter = logging.Formatter(logformat)
hdl = logging.StreamHandler(); hdl.setFormatter(formatter); LOG.addHandler(hdl)


# Launch database connection
with Db(db_type='sync', db_file='%s/db.json' % ARGS.target, dry_run=DRY_RUN) as db:
    # Create target dir
    create_dir(ARGS.target, dry_run=DRY_RUN)
    # For each files
    for dir_path, dirs, files in os.walk(ARGS.source):
        if not files: continue
        for file_name in files:
            file_path = os.path.join(dir_path, file_name)
            if db.get(file_path) is None:
                LOG.warning('Copy file %s' % file_path)
                # TODO factorize get source dest -> make dest dir add filename at copy
                file_source = os.path.join(dir_path, file_name)
                # Dest is same path without root dir
                dir_dst = os.path.join(ARGS.target,
                                       re.sub(r'%s/?' % ARGS.source,'',dir_path))
                print '%s -> %s' % (file_source, dir_dst)
                dir_dst = os.path.join(ARGS.target,dir_path)
                create_dir(dir_dst, dry_run=DRY_RUN)

                db.save(file_path, 'unused')

        #print [(fname, hashlib.md5(open('%s/%s' % (dirnpath, fname), 'rb').read()).digest()) for fname in filenames]

    print db.get('key')
    print db.get_all()
    db.flush_all()





# Clean empty dir after sync
remove_empty_dir(ARGS.target, dry_run=DRY_RUN)
# WALK
    #import hashlib
    #for dirnpath, dirnames, filenames in os.walk('Videos'):
        #print dirnpath, filenames
        #if not filenames: continue
        #print [(fname, hashlib.md5(open('%s/%s' % (dirnpath, fname), 'rb').read()).digest()) for fname in filenames]
# Copy with progress http://stackoverflow.com/questions/274493/how-to-copy-a-file-in-python-with-a-progress-bar

# DATABASE
#    with Db(db_file='/tmp/db.json') as db:
#        db.save('key', 'value')
#        print db.get('key')
#        print db.get_all()
