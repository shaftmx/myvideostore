#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from myvideostore.tools import Print
import argparse

# Init logging level with debug stream handler
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

# TODO
#  * Prendre en arg un dossier src et un dst
#  * Faire un fichier db à la racine de ce dossier dst
#  * La db va contenir le path et un hash du fihier et status (copied)
#  * Possible d'ajouter des excludes pour les dossiers.
#  * copier les nouveaux fichiers et reconstruire l'arbo
#  * Apres passage du sync clean des dossiers vides
#  * + Ajouter la liste des nouvelles videos dans la db du videostore

