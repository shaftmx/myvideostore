#!/usr/bin/env python

from distutils.core import setup

setup(name='myvideostore',
      version='0.1',
      description=('Small cli script to Sync only new video in your server. '
            'Allow include et exclude rules. '
            'Browse your video directory, tag viewed video and launch vlc'),
      author='gaelL',
      author_email='gael@netwiki.fr',
      url='https://github.com/shaftmx/myvideostore',
      packages=['myvideostore'],
      scripts=['myvideostore-sync-new-files.py', 'myvideostore-launch.py'],
     )
