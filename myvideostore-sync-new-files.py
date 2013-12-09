#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from myvideostore.tools import Print
import argparse
import os


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


def create_dir(path):
    if DRY_RUN:
        LOG.warning('Create directory : %s' % path)
    else:
        if not os.path.isdir(path):
            LOG.info('Create directory : %s' % path)
            os.makedirs(path)
    
create_dir('bla')



def remove_empty_dir(path):
    # Set dry-run hack
    deleted_dir = []
    # Run while dir are remove
    all_cleaned = False
    while not all_cleaned:
        all_cleaned = True
        for root, dirs, files in os.walk(path,topdown=False):
            for name in dirs:
                fname = os.path.join(root,name)
                # Check if dir is empty or in case of dryrun if the dir is not
                # marked deleted
                if not os.listdir(fname) and (fname not in deleted_dir):
                    if DRY_RUN:
                        deleted_dir.append(fname)
                    else:
                        #os.removedirs(fname)
                        pass
                    LOG.info('Delete empty directory : %s' % fname)
                    all_cleaned = False
                elif DRY_RUN and os.listdir(fname):
                    # Check if dir content are only file or dir marked in deleted_dir
                    # In case of all dir or file are marked, the dir will be deleted (empty)
                    dir_content = os.listdir(fname)
                    for content_name in dir_content:
                        if os.path.join(fname, content_name) in deleted_dir:
                            dir_content.remove(content_name)
                    if not dir_content and not fname in deleted_dir:
                        deleted_dir.append(fname)
                        LOG.info('Delete empty directory : %s' % fname)
    print deleted_dir

remove_empty_dir('Videos')
# Excepted -> empty, empty2/empty_sub, empty2
