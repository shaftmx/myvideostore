#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import logging
from myvideostore.tools import Print


# Init logging level with debug stream handler
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


Print.red('bla')

# TODO
#  * Prendre en arg un dossier
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


def init_curses():
   stdscr = curses.initscr()
   curses.noecho()
   curses.cbreak()
   stdscr.keypad(1)
   return stdscr


def close_curses(stdscr):
  stdscr.keypad(0)
  curses.nocbreak()
  curses.echo()
  curses.endwin()


def init_colors():
  curses.start_color()
  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)


def display_menu(title, menu, window, active=1):
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


def getkey(final, title, menu, window, active_pos = 1):
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
    display_menu(title, menu, window, active_pos)

  return active_pos


if __name__ == "__main__":
    from myvideostore.db import Db
    with Db(db_file='/tmp/db.json') as db:
        db.save('key', 'value')
        print db.get('key')
        print db.get_all()
        
#  try:
#    # Initialisation de curses
#    stdscr = init_curses()
#
#    # Initialisation des couleurs
#    init_colors()
#
#    # Création de la sous-fenêtre
#    window = stdscr.subwin(40, 79, 3, 5)
#    window.border(0)
#
#    menu_list = ("Choix 1", "Choix 2", "Choix 3", "Quitter")
#    title = "Petit test de menu"
#    display_menu(title, menu_list, window)
#
#    choice = getkey(len(menu_list), title, menu_list, window)
#    window.addstr(len(menu_list) + 5, 1,
#        "Choix de l'utilisateur : %s (%d)" % (menu_list[choice-1], choice))
#    window.addstr(len(menu_list) + 6, 1, "Appuyez sur une touche pour sortir")
#    window.refresh()
#    c = window.getch()
#  finally:
#    #Fermeture de curses
#    close_curses(stdscr)
#
