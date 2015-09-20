#!/usr/bin/env python

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
