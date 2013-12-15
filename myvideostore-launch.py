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
LOG.setLevel(logging.INFO)
logformat =  '%(asctime)s %(levelname)s -: %(message)s'
# Set logger formater
formatter = logging.Formatter(logformat)
#hdl = logging.StreamHandler(); hdl.setFormatter(formatter); LOG.addHandler(hdl)
hdl = logging.FileHandler('/tmp/log'); hdl.setFormatter(formatter); LOG.addHandler(hdl)

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
        curses.curs_set(0) # make cursor invisible
        return stdscr
    
    
    def _close_curses(self, stdscr):
      stdscr.keypad(0)
      curses.nocbreak()
      curses.echo()
      curses.endwin()
    
    
    def _init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
        self._color_video_viewed  = curses.color_pair(1)
        self._color_video = curses.A_NORMAL
        self._color_directory = curses.color_pair(3) | curses.A_BOLD
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        #curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        #self._window.addstr(0, 0, "Current mode: Typing mode", curses.A_REVERSE)
        #self._window.addstr(0, 0, "Current mode: Typing mode", curses.A_UNDERLINE)
        #self._window.addstr(0, 0, "Current mode: Typing mode", curses.A_BOLD)
        #self._window.addstr(0, 0, "Current mode: Typing mode", curses.A_BLINK)
    
    
    def _display_menu(self, title, menu, active=1):
        # Window title
        self._window.addstr(0, 0, os.path.basename(__file__), curses.A_NORMAL | curses.A_BOLD)
        # Title
        self._window.addstr(1, 1, title, curses.color_pair(1))
        self._window.addstr(3, 1, "Sélectionnez une entrée...")

        item_pos = 4
        pos = 1
        for item in menu:
            if item['type'] == 'file':
                color = self._color_video
            else:
                color = self._color_directory
             
            if pos == active:
                color |= curses.A_UNDERLINE
                #color |= curses.A_UNDERLINE | curses.A_BOLD

            self._window.addstr(item_pos, 1, "    %d. %s" % (pos, item['name']), color)
            item_pos += 1
            pos += 1
    
        self._window.refresh()
    
    
    def _getkey(self, final, title, menu, active_pos = 1):
        # int to key chr(10) Inverse str -> int ord('\n')
        # LOG.critical('Key : %s' % c)
        # Key mapping
        KEY_ENTER = 10
        KEY_UP = 65
        KEY_DOWN = 66
        KEY_LEFT = 68
        KEY_RIGHT = 67
        c = None
        while c != KEY_ENTER:
            c = self._window.getch()
            if c == KEY_DOWN:
              if active_pos != final:
                active_pos += 1
              else:
                active_pos = 1
            elif c == KEY_UP:
              if active_pos != 1:
                active_pos -= 1
              else:
                active_pos = final
            self._display_menu(title, menu, active_pos)
        return active_pos

    def _grouper(self, iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    def _paginate(self, iterable, lines=10):
        "Used to paginate"
        class Pages(object):
            "Manage menu pages"
            def __init__(self, pages):
                self._pages = pages
                self._current = 0
                self._total = len(self._pages)
            def get_content(self):
                return self._pages[self._current]
            def next(self):
                if self._current < (self._total - 1):
                    self._current += 1
            def previous(self):
                if self._current > 0:
                    self._current -= 1
        return Pages([ page for page in self._grouper(iterable, lines)])

    def _dir_explore(self, directory):
        dir_path = ARGS.directory
        files = []
        dirs = []
        for filename in os.listdir(directory):
            if os.path.isdir('%s/%s' % (dir_path, filename)):
                dirs.append({'name': filename, 'type': 'directory'})
            if os.path.isfile('%s/%s' % (dir_path, filename)):
                dirs.append({'name': filename, 'type': 'file', 'marked': True})
        return [{'name': '..', 'type': 'directory'}] + sorted(dirs) + sorted(files)


    def launch_curses(self):
        #directory_pages = self._paginate(self._dir_explore(ARGS.directory), 2)
        #for line in directory_pages.get_content():
        #    print ' * %s' % line['name']
        #directory_pages.next()
        #print directory_pages.get_content()
        try:
            # Initialisation de curses
            stdscr = self._init_curses()
    
            # Initialisation des couleurs
            self._init_colors()
    
            # Création de la sous-fenêtre
            self._window = stdscr.subwin(40, 90, 3, 5)
            self._window.border(0)

            # All this things in _getkey ---------
            # Display navigate menu
            directory_pages = self._paginate(self._dir_explore(ARGS.directory), 4)
            menu_list = directory_pages.get_content()
            #directory_pages.next()

            title = ARGS.directory
            self._display_menu(title, menu_list)
    
            choice = self._getkey(len(menu_list), title, menu_list)
            self._window.addstr(len(menu_list) + 5, 1,
                "Choix de l'utilisateur : %s (%d)" % (menu_list[choice-1], choice))
            self._window.addstr(len(menu_list) + 6, 1, "Appuyez sur une touche pour sortir")
            self._window.refresh()
            c = self._window.getch()
            # -------------------
        finally:
            #Fermeture de curses
            self._close_curses(stdscr)

# ./myvideostore-launch.py -d Videos.tests/
if __name__ == "__main__":

    #Print.red('bla')
    gui = NavCurses()
    gui.launch_curses()
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

