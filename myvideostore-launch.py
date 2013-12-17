#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import curses
import logging
import argparse
from myvideostore.tools import Print, len_without_none
from myvideostore.db import Db
from itertools import izip_longest
from os.path import join, dirname


# TODO
#X  * Prendre en arg un dossier
#  * Faire un fichier db à la racine de ce dossier
#  * La db va contenir le status (vue ou non) et les nouvelles videos
#  * Le menu permettera de :
#    * Refresh les video (ou auto quand on entre dans un dossier maxdepth 1)
#X    * Naviguer dans les dossiers
#    * Rendre vu ou non une video
#    * Lancer vlc et rendre vu cette video
#    * + Supprimer une video du disque
#      * si le dossier est vide supprimer le dossier aussi
#    * Afficher les nouvelles videos (entrée par le dernier sync)
#  * Display help at last line of the screen
#  * Get screen width and height in var and generate dynamic display

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

    def _init_window(self):
            self._window.border(0)

    def _display_menu(self, title, page, active_pos=1):
        # Init window in case of clean
        self._init_window()

        # Window title
        self._window.addstr(0, 0, os.path.basename(__file__), curses.A_NORMAL | curses.A_BOLD)
        # Title
        self._window.addstr(1, 1, title, curses.color_pair(1))
        self._window.addstr(3, 1, "Sélectionnez une entrée...")

        item_pos = 4
        pos = 1
        for item in page:
            if item is None: continue
            if item['type'] == 'file':
                color = self._color_video
            else:
                color = self._color_directory
             
            if pos == active_pos:
                color |= curses.A_UNDERLINE
                #color |= curses.A_UNDERLINE | curses.A_BOLD

            self._window.addstr(item_pos, 1, "    %d. %s" % (pos, item['name']), color)
            item_pos += 1
            pos += 1
    
        self._window.refresh()
    
    
    def _launch_app(self):

        # Init window
        self._init_window()

        # All this things in _getkey ---------
        # Display navigate menu
        #directory_pages.next()

        title = ARGS.directory
    
        #choice = self._getkey(len(page), title, page)
        #self._window.addstr(len(page) + 5, 1,
        #    "Choix de l'utilisateur : %s (%d)" % (page[choice-1], choice))
        #self._window.addstr(len(page) + 6, 1, "Appuyez sur une touche pour sortir")
        #self._window.refresh()
        #c = self._window.getch()
        # -------------------
        # int to key chr(10) Inverse str -> int ord('\n')
        # LOG.critical('Key : %s' % c)
        # Key mapping
        KEY_RETURN = 127
        KEY_DEL = 126
        KEY_ENTER = 10
        KEY_UP = 65
        KEY_DOWN = 66
        KEY_LEFT = 68
        KEY_RIGHT = 67
        KEY_Q = 113
        KEY_SPACE = 32
        c = None
        active_pos = 1
        # Get dir content
        current_relativ_dir = ''
        directory_pages = self._paginate(self._dir_explore(ARGS.directory),
                                         lines=4)
        page = directory_pages.get_content()
        while c != KEY_Q:
            #LOG.critical('%s' % c)

            # Get selected item
            item = page[active_pos - 1]

            if c == KEY_DOWN:
              if active_pos < len_without_none(page):
                active_pos += 1
              else:
                active_pos = 1
            elif c == KEY_UP:
              if active_pos > 1:
                active_pos -= 1
              else:
                active_pos = len_without_none(page)
            elif c == KEY_RIGHT:
                # Change directory page and get content
                directory_pages.next()
                page = directory_pages.get_content()
                # Clear screen
                self._window.clear()
                active_pos = 1
            elif c == KEY_LEFT:
                # Change directory page and get content
                directory_pages.previous()
                page = directory_pages.get_content()
                # Clear screen
                self._window.clear()
                active_pos = 1
            elif c in [KEY_RETURN, KEY_DEL]:
                if item['type'] == 'file':
                    LOG.critical('Delete file %s' % join(ARGS.directory, current_relativ_dir, item['name']))
            elif c == KEY_SPACE:
                if item['type'] == 'file':
                    LOG.critical('Mark video file %s' % join(ARGS.directory, current_relativ_dir, item['name']))
            elif c == KEY_ENTER:
                if item['type'] == 'directory':
                    # Change current dir
                    if item['name'] == '..':
                        current_relativ_dir = dirname(current_relativ_dir)
                    else:
                        current_relativ_dir = join(current_relativ_dir, item['name'])
                    # explore new dir
                    directory_pages = self._paginate(
                                            self._dir_explore(join(ARGS.directory, current_relativ_dir)),
                                            lines=4)
                    # Paginate the content
                    page = directory_pages.get_content()
                    # Clear screen
                    self._window.clear()
                    active_pos = 1
                else:
                    LOG.critical('Launch vlc on %s' % join(ARGS.directory, current_relativ_dir, item['name']))
            
            self._display_menu(title, page, active_pos)

            # Pages status
            self._window.addstr(len(page) + 6, 1,
                    "Page %s/%s" % (directory_pages._current, directory_pages._total))
            # Get key
            c = self._window.getch()
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
                self._total = len(self._pages) - 1
            def get_content(self):
                return self._pages[self._current]
            def next(self):
                if self._current < self._total:
                    self._current += 1
            def previous(self):
                if self._current > 0:
                    self._current -= 1
        return Pages([ page for page in self._grouper(iterable, lines)])

    def _dir_explore(self, directory):
        dir_path = directory
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
    
            self._launch_app()

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

