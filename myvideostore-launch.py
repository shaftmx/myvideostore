#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import curses
import logging
import argparse
from myvideostore.tools import Print
from myvideostore.db import Db
from itertools import izip_longest


# TODO
#X  * Prendre en arg un dossier
#  * Faire un fichier db à la racine de ce dossier
#  * La db va contenir le status (vue ou non) et les nouvelles videos
#  * Le menu permettera de :
#    * Refresh les video (ou auto quand on entre dans un dossier maxdepth 1)
#    * Naviguer dans les dossiers
#    * Rendre vu ou non une video
#    * Lancer vlc et rendre vu cette video
#    * + Supprimer une video du disque
#    * Afficher les nouvelles videos (entrée par le dernier sync)
#    * si le dossier est vide supprimer le dossier aussi

# Init logging level with debug stream handler
LOG = logging.getLogger()
LOG.setLevel(logging.CRITICAL)
LOG.setLevel(logging.INFO)

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-d", "--directory",
            help="Directory where you browse videos",
            type=str,
            required=True)
ARGS = PARSER.parse_args()


class NavCurses(object):

    def __init__(self):
        pass

    def _init_curses(self):
       stdscr = curses.initscr()
       curses.noecho()
       curses.cbreak()
       stdscr.keypad(1)
       return stdscr
    
    
    def _close_curses(self, stdscr):
      stdscr.keypad(0)
      curses.nocbreak()
      curses.echo()
      curses.endwin()
    
    
    def _init_colors(self):
      curses.start_color()
      curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
      curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    
    
    def _display_menu(self, title, menu, window, active=1):
      window.addstr(1, 1, title, curses.color_pair(1))
      window.addstr(3, 1, "Sélectionnez une entrée...")
      item_pos = 4
      pos = 1
      for item in menu:
        if pos == active:
          color = curses.color_pair(2)
        else:
          color = curses.A_NORMAL
        window.addstr(item_pos, 1, "    %d. %s" % (pos, item), color)
        item_pos += 1
        pos += 1
    
      window.refresh()
    
    
    def _getkey(self, final, title, menu, window, active_pos = 1):
      c = None
    
      while c != 10:
        c = window.getch()
        if c == 66:
          if active_pos != final:
            active_pos += 1
          else:
            active_pos = 1
        elif c == 65:
          if active_pos != 1:
            active_pos -= 1
          else:
            active_pos = final
        self._display_menu(title, menu, window, active_pos)
    
      return active_pos

    def _grouper(self, iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    def _paginate(self, iterable, lines=10):
        "Used to paginate"
        return [ page for page in self._grouper(iterable, lines)]

    def launch_curses(self):
      try:
        # Initialisation de curses
        stdscr = self._init_curses()
    
        # Initialisation des couleurs
        self._init_colors()
    
        # Création de la sous-fenêtre
        window = stdscr.subwin(40, 90, 3, 5)
        window.border(0)

        # Display navigate menu
        menu_list = ("Choix 1", "Choix 2", "Choix 3", "Quitter")
        title = ARGS.directory
        self._display_menu(title, menu_list, window)
    
        choice = self._getkey(len(menu_list), title, menu_list, window)
        window.addstr(len(menu_list) + 5, 1,
            "Choix de l'utilisateur : %s (%d)" % (menu_list[choice-1], choice))
        window.addstr(len(menu_list) + 6, 1, "Appuyez sur une touche pour sortir")
        window.refresh()
        c = window.getch()
      finally:
        #Fermeture de curses
        self._close_curses(stdscr)

# ./myvideostore-launch.py -d Videos.tests/
if __name__ == "__main__":

    #Print.red('bla')
    gui = NavCurses()
    #gui.launch_curses()

### FILE
    dir_path = ARGS.directory
    files = []
    dirs = []
    for filename in os.listdir(dir_path):
        if os.path.isdir('%s/%s' % (dir_path, filename)):
            print 'Dir : %s' % filename
            dirs.append({'name': filename, 'type': 'directory'})
        if os.path.isfile('%s/%s' % (dir_path, filename)):
            print 'file : %s' % filename
            dirs.append({'name': filename, 'type': 'file', 'marked': True})
    dir_contents = [{'name': '..', 'type': 'directory'}] + sorted(dirs) + sorted(files)
    print gui._paginate(dir_contents, 3)

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

