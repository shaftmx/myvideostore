#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
                     '--add-include "^bar"')
        self.run_cmd('./myvideostore-sync-new-files.py -s ./Videos.tests -t ./Videos_dest.tests')
        dir_dest = self.run_cmd('find ./Videos_dest.tests ! -name db.json -printf "%P\n"')
        self.assertEquals(sorted(dir_expected), sorted(dir_dest))

if __name__ == '__main__':
    unittest.main()
