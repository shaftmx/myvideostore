#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Gaël Lambert (gaelL) <gael.lambert@netwiki.fr>
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

import unittest2 as unittest

import mox
import stubout
import os, sys
import mock
import subprocess

class TestCase(unittest.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.mox = mox.Mox()
        self.stubs = stubout.StubOutForTesting()

    def tearDown(self):
        self.mox.UnsetStubs()
        self.stubs.UnsetAll()
        self.stubs.SmartUnsetAll()
        self.mox.VerifyAll()
        super(TestCase, self).tearDown()

    def run_cmd(self, cmd):
        stdout = subprocess.Popen('%s 2>/dev/null' % cmd,
                                  shell=True,
                                  stdout=subprocess.PIPE)
        return [line for line in stdout.communicate()[0].split('\n') if line != '']

class Sync_new_files_TestCase(TestCase):

    def setUp(self):
        super(Sync_new_files_TestCase, self).setUp()
        # Delete dest dir just in case
        self.run_cmd('rm -rf ./Videos_dest.tests')
        self.run_cmd('rm -rf "./Videos.tests/bar/s1/2"')

    def tearDown(self):
        super(Sync_new_files_TestCase, self).tearDown()
        # Delete dest dir just in case
        self.run_cmd('rm -rf ./Videos_dest.tests')
        self.run_cmd('rm -rf "./Videos.tests/bar/s1/2"')

    def test_basic_sync(self):
        dir_expected = [
                    'bar',
                    'bar/s1',
                    'bar/s1/1',
                    'space dir',
                    'space dir/episode 1',
                    'blé'
                   ]
        # Lunch first sync with all files
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        self.assertEquals(sorted(dir_expected), sorted(dir_dest))

        # Remove space dir and lunch script
        self.run_cmd('rm -rf "./Videos_dest.tests/bar"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        dir_expected.remove('bar')
        dir_expected.remove('bar/s1')
        dir_expected.remove('bar/s1/1')
        self.assertEquals(sorted(dir_expected), sorted(dir_dest))
        
        # Add new file 2 in bar/s1. Must copy only this file
        self.run_cmd('touch "./Videos.tests/bar/s1/2"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        dir_expected.append('bar')
        dir_expected.append('bar/s1')
        dir_expected.append('bar/s1/2')
        self.assertEquals(sorted(dir_expected), sorted(dir_dest))

    def test_basic_exclude(self):
        dir_expected = [
                    'bar',
                    'bar/s1',
                    'bar/s1/1',
                    'blé'
                   ]

        # Exlude one dir
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--add-exclude "^space dir/?.*"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        self.assertEquals(sorted(dir_expected), sorted(dir_dest))
        # Delete exclude
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--del-exclude 0')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        dir_expected.append('space dir')
        dir_expected.append('space dir/episode 1')
        self.assertEquals(sorted(dir_expected), sorted(dir_dest))


    def test_basic_include(self):
        dir_expected = [
                    'bar',
                    'bar/s1',
                    'bar/s1/1',
                   ]
        # Exlude all and control it's all exclude
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--add-exclude ".*"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        self.assertEquals(sorted([]), sorted(dir_dest))

        # Include bar
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--add-include "^bar/"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        self.assertEquals(sorted(dir_expected), sorted(dir_dest))

    def test_basic_pre_cmd(self):
        # pre cmd create file
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--pre "touch ./Videos_dest.tests/pre_cmd"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests -name pre_cmd -printf "%P\n"')
        self.assertEquals(sorted(['pre_cmd']), sorted(dir_dest))

    def test_basic_post_cmd(self):
        # post cmd create file
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--post "touch ./Videos_dest.tests/post_cmd"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests -name post_cmd -printf "%P\n"')
        self.assertEquals(sorted(['post_cmd']), sorted(dir_dest))

    def test_basic_pre_post_cmd_error(self):
        # Launch pre cmd error script must exit so no post cmd
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--post "touch ./Videos_dest.tests/post_cmd" '
                     '--pre "false"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests -name "*_cmd" -printf "%P\n"')
        self.assertEquals(sorted([]), sorted(dir_dest))

        # Launch post cmd error script must exit so only pre cmd executed
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--post "false" '
                     '--pre "touch ./Videos_dest.tests/pre_cmd"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests -name "*_cmd" -printf "%P\n"')
        self.assertEquals(sorted(['pre_cmd']), sorted(dir_dest))

    def test_basic_pre_post_cmd(self):
        # Launch pre and post cmd
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests '
                     '-t ./Videos_dest.tests '
                     '--post "touch ./Videos_dest.tests/post_cmd" '
                     '--pre "touch ./Videos_dest.tests/pre_cmd"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests -name "*_cmd" -printf "%P\n"')
        self.assertEquals(sorted(['post_cmd','pre_cmd']), sorted(dir_dest))

    def test_db_purge(self):
        # First list before db -> empty
        result = self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests --db-list')
        self.assertEquals(result,[])

        # Launch one sync and list files
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        result = self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests --db-list')
        self.assertTrue(' - bar/s1/1' in result)
        # Remove db entry bar and list without bar
        self.run_cmd('echo y | ./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests --db-purge "^bar"')
        result = self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests --db-list')
        self.assertTrue(' - bar/s1/1' not in result and result)


if __name__ == '__main__':
    unittest.main()
