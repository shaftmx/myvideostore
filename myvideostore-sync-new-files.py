#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from myvideostore.tools import Print
from myvideostore.tools import create_dir, remove_empty_dir
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


# Clean empty dir after sync
remove_empty_dir(ARGS.target, dry_run=DRY_RUN)

create_dir(ARGS.target, dry_run=DRY_RUN)
