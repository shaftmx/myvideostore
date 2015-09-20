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

import os
import curses
import logging
import argparse
import subprocess
from myvideostore.tools import Print, len_without_none, Keycode, remove_empty_dir
from myvideostore.db import Db
from itertools import izip_longest
from os.path import join, dirname

# Force locales to fixe curses and accent display
# http://www.gossamer-threads.com/lists/python/python/544338?do=post_view_threaded#544338
import locale
#locale.setlocale(locale.LC_ALL,"fr_FR.UTF-8")
locale.setlocale(locale.LC_ALL,"en_US.UTF-8")


# Init logging level with debug stream handler
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
logformat =  '%(asctime)s %(levelname)s -: %(message)s'
# Set logger formater
formatter = logging.Formatter(logformat)
#hdl = logging.StreamHandler(); hdl.setFormatter(formatter); LOG.addHandler(hdl)
hdl = logging.FileHandler('/tmp/%s.log' % __name__); hdl.setFormatter(formatter); LOG.addHandler(hdl)

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-d", "--directory",
            help="Directory where you browse videos",
            type=str,
            required=True)
ARGS = PARSER.parse_args()


class Pages(object):
    "Manage page for things like (['1', '2', '3'], ['4', '5', '6'])"
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

class NavCurses(object):

    def __init__(self, width, height):
        self._width = width
        self._height = height

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

    def _display_help(self):
        sub_height = self._height - 6
        sub_width = self._width - 6
        sub = self._window.subwin( sub_height, sub_width, 6, 8)
        sub.clear()
        sub.border(0)
        # 4, 4 for the corner
        self._window.addstr( 6, 41, "Help")
        self._window.addstr( 11, 20, "h / help")
        self._window.addstr( 13, 20, "q / exit")
        self._window.addstr( 15, 20, "v / launch vlc")
        self._window.addstr( 11, 42, "left,right / change page")
        self._window.addstr( 13, 42, "return,del / delete video")
        self._window.addstr( 15, 42, "space      / mark video as viewed")
        sub.refresh()
        # Pause
        sub.getch()
        # Clear screen
        sub.clear()

    def _display_del_confirm(self, filename):
        sub_height = self._height - 6
        sub_width = self._width - 6
        sub = self._window.subwin( sub_height, sub_width, 6, 8)
        sub.clear()
        sub.border(0)
        # 4, 4 for the corner
        self._window.addstr( 6, 12, "Really want to delete this file y/N ?")
        self._window.addstr( 8, 12, "File : %s" % filename)
        sub.refresh()
        # Clear screen
        # y : 121
        c = sub.getch()
        sub.clear()
        if c == 121:
            return True
        return False

    def _display_menu(self, title, page, active_pos=1):
        # Init window in case of clean
        self._init_window()
        # Window title
        self._window.addstr(0, 0, os.path.basename(__file__), curses.A_NORMAL | curses.A_BOLD)
        # Title
        self._window.addstr(1, 1, title, curses.color_pair(1))
        self._window.addstr(3, 1, "Sélectionnez une entrée...")
        # Display usage
        self._window.addstr(self._height - 2 , 1, "Usage : q/exit   h/help   v/vlc")

        item_pos = 4
        pos = 1
        for item in page:
            if item is None: continue
            if item['type'] == 'file':
                if item['marked']:
                    color = self._color_video_viewed
                else:
                    color = self._color_video
            else:
                color = self._color_directory
            if pos == active_pos:
                color |= curses.A_UNDERLINE
                #color |= curses.A_UNDERLINE | curses.A_BOLD
            self._window.addstr(item_pos, 1, "    - %s" % (item['name']), color)
            #self._window.addstr(item_pos, 1, "    %d. %s" % (pos, item['name']), color)
            item_pos += 1
            pos += 1
        self._window.refresh()
    
    def _launch_app(self):
        # Init window
        self._init_window()
        title = ARGS.directory

        # Key mapping
        key = Keycode()
        c = None
        active_pos = 1
        # Get dir content
        line_number=30
        current_relativ_dir = ''
        directory_pages = self._paginate(self._dir_explore(root=ARGS.directory, directory=''),
                                         lines=line_number)
        page = directory_pages.get_content()
        while c != key.code_q:
            #LOG.critical('%s' % c)

            # Get selected item
            item = page[active_pos - 1]

            # -- DOWN
            if c == key.code_down:
              if active_pos < len_without_none(page):
                active_pos += 1
              else:
                active_pos = 1
            # -- UP
            elif c == key.code_up:
              if active_pos > 1:
                active_pos -= 1
              else:
                active_pos = len_without_none(page)
            # -- RIGHT
            elif c == key.code_right:
                # Change directory page and get content
                directory_pages.next()
                page = directory_pages.get_content()
                # Clear screen
                self._window.clear()
                active_pos = 1
            # -- LEFT
            elif c == key.code_left:
                # Change directory page and get content
                directory_pages.previous()
                page = directory_pages.get_content()
                # Clear screen
                self._window.clear()
                active_pos = 1
            # -- H
            elif c == key.code_h:
                self._display_help()
            # -- RETURN or DEL
            elif c in [key.code_return, key.code_del]:
                if item is not None and item.get('type') == 'file' \
                and self._display_del_confirm(item['name']):
                    # Unmark if marked
                    if item['marked']:
                        with Db(db_name='library', db_file='%s/db.json' % ARGS.directory) as db:
                            db.remove(join(current_relativ_dir, item['name']))
                    # Delete file
                    os.remove(join(ARGS.directory, current_relativ_dir, item['name']))
                    # Launch empty dir clean
                    remove_empty_dir(ARGS.directory)
                    # In case your current dir is remove goto root dir
                    if not os.path.isdir(join(ARGS.directory, current_relativ_dir)):
                        current_relativ_dir = ''

                    # Refresh explore
                    directory_pages = self._paginate(
                                            self._dir_explore(root=ARGS.directory, directory=current_relativ_dir),
                                            lines=line_number)
                    # Paginate the content
                    page = directory_pages.get_content()
                    self._window.clear()
            # -- SPACE
            elif c == key.code_space:
                if item.get('type') == 'file':
                    # mark as viewed
                    with Db(db_name='library', db_file='%s/db.json' % ARGS.directory) as db:
                        # Unmark
                        if db.get(join(current_relativ_dir,item['name'])):
                            db.remove(join(current_relativ_dir,item['name'].decode('utf-8')))
                            item['marked'] = False
                        # Mark
                        else:
                            db.save(join(current_relativ_dir,item['name']), 'unused')
                            item['marked'] = True
            # -- ENTER
            elif c == key.code_enter:
                if item.get('type') == 'directory':
                    # Change current dir
                    if item['name'] == '..':
                        current_relativ_dir = dirname(current_relativ_dir)
                    else:
                        current_relativ_dir = join(current_relativ_dir, item['name'])
                    # explore new dir
                    directory_pages = self._paginate(
                                            self._dir_explore(root=ARGS.directory, directory=current_relativ_dir),
                                            lines=line_number)
                    # Paginate the content
                    page = directory_pages.get_content()
                    # Clear screen
                    self._window.clear()
                    active_pos = 1
            # -- V
            elif c == key.code_v:
                video_path = join(ARGS.directory, current_relativ_dir, item['name'])
                LOG.warning('Launch vlc on %s' % video_path)
                subprocess.call("vlc '%s'" % video_path, shell=True)
                self._window.clear()

            # Display menu
            self._display_menu(title, page, active_pos)

            # Pages status
            self._window.addstr(len(page) + 6, 1,
                    " -- Page %s/%s" % (directory_pages._current, directory_pages._total))
            # Get key
            c = self._window.getch()
        return active_pos

    def _grouper(self, iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    def _paginate(self, iterable, lines=10):
        "Used to paginate directory contnent"
        return Pages([ page for page in self._grouper(iterable, lines)])

    def _dir_explore(self, root, directory):
        "Explore directory and return content"
        dir_path = join(root, directory)
        files = []
        dirs = []
        for filename in os.listdir(dir_path):
            if os.path.isdir(join(dir_path, filename)):
                dirs.append({'name': filename, 'type': 'directory'})
            # Filter db file
            if os.path.isfile(join(dir_path, filename)) and filename != 'db.json':
                # Marked or not ?
                with Db(db_name='library', db_file='%s/db.json' % root) as db:
                    if db.get(join(directory, filename)):
                        marked = True
                    else:
                        marked = False
                files.append({'name': filename, 'type': 'file', 'marked': marked})
        return [{'name': '..', 'type': 'directory'}] + sorted(dirs, key=lambda name: name['name']) + sorted(files, key=lambda name: name['name'])


    def launch_curses(self):
        try:
            # Initialisation de curses
            stdscr = self._init_curses()
    
            # Initialisation des couleurs
            self._init_colors()

            # Création de la sous-fenêtre
            self._window = stdscr.subwin( self._height, self._width, 3, 5)
    
            self._launch_app()

        except curses.error:
            ERROR = 'Error : terminal size too small'
        finally:
            #Fermeture de curses
            self._close_curses(stdscr)
            if 'ERROR' in vars():
                LOG.critical(ERROR)
                print ERROR
            

# ./myvideostore-launch.py -d Videos.tests/
if __name__ == "__main__":
    gui = NavCurses(width=90, height=40)
    gui.launch_curses()
