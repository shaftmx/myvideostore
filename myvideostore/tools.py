#!/usr/bin/env python
# -*- coding: utf-8 -*- 

class Print(object):
    @staticmethod
    def white(texte):
        print "\033[37m%s\033[0m" % texte

    @staticmethod
    def grey(texte):
        print "\033[30m%s\033[0m" % texte
     
    @staticmethod
    def grey_strong(texte):
        print "\033[1;30m%s\033[0m" % texte
     
    @staticmethod
    def blue(texte):
        print "\033[34m%s\033[0m" % texte
     
    @staticmethod
    def red(texte):
        print "\033[31m%s\033[0m" % texte
     
    @staticmethod
    def green(texte):
        print "\033[32m%s\033[0m" % texte
     
    @staticmethod
    def pink(texte):
        print "\033[35m%s\033[0m" % texte
     
    @staticmethod
    def yellow(texte):
        print "\033[33m%s\033[0m" % texte
     
    @staticmethod
    def cyan(texte):
        print "\033[36m%s\033[0m" % texte
