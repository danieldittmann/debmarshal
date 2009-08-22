#!/usr/bin/python
# -*- python-indent: 2; py-indent-offset: 2 -*-
# Copyright 2009 Google Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""tests for debmarshal.distros.base."""


__authors__ = [
    'Evan Broder <ebroder@google.com>',
]


import os
import shutil
import subprocess
import tempfile
import unittest

import mox
import pkg_resources

from debmarshal.distros import base
from debmarshal import errors


class TestCaptureCall(mox.MoxTestBase):
  def testPassStdin(self):
    mock_p = self.mox.CreateMock(subprocess.Popen)
    self.mox.StubOutWithMock(subprocess, 'Popen', use_mock_anything=True)

    subprocess.Popen(['ls'],
                     stdin='foo',
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT).AndReturn(
        mock_p)
    mock_p.communicate(None).AndReturn(('bar', 'baz'))
    mock_p.returncode = 0

    self.mox.ReplayAll()

    self.assertEqual(base.captureCall(['ls'], stdin='foo'),
                     'bar')

  def testPassStdout(self):
    mock_p = self.mox.CreateMock(subprocess.Popen)
    self.mox.StubOutWithMock(subprocess, 'Popen', use_mock_anything=True)

    subprocess.Popen(['ls'],
                     stdin=subprocess.PIPE,
                     stdout='blah',
                     stderr=subprocess.STDOUT).AndReturn(
        mock_p)
    mock_p.communicate(None).AndReturn((None, None))
    mock_p.returncode = 0

    self.mox.ReplayAll()

    self.assertEqual(base.captureCall(['ls'], stdout='blah'),
                     None)

  def testPassStderr(self):
    mock_p = self.mox.CreateMock(subprocess.Popen)
    self.mox.StubOutWithMock(subprocess, 'Popen', use_mock_anything=True)

    subprocess.Popen(['ls'],
                     stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE,
                     stderr='foo').AndReturn(
        mock_p)
    mock_p.communicate(None).AndReturn(('bar', 'baz'))
    mock_p.returncode = 0

    self.mox.ReplayAll()

    self.assertEqual(base.captureCall(['ls'], stderr='foo'),
                     'bar')

  def testError(self):
    mock_p = self.mox.CreateMock(subprocess.Popen)
    self.mox.StubOutWithMock(subprocess, 'Popen', use_mock_anything=True)

    subprocess.Popen(['ls'],
                     stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT).AndReturn(
        mock_p)
    mock_p.communicate(None).AndReturn((None, None))
    mock_p.returncode = 255

    self.mox.ReplayAll()

    self.assertRaises(subprocess.CalledProcessError, base.captureCall, ['ls'])


class TestCreateSparseFile(unittest.TestCase):
  """Test creating sparse files.

  For once, this has well enough defined behavior that we can actually
  test ends instead of means.
  """
  def testCreateFile(self):
    fd, name = tempfile.mkstemp()
    os.close(fd)
    size = 1024 ** 2

    base.createSparseFile(name, size)

    try:
      self.assertEqual(os.stat(name).st_size, size)
      self.assertEqual(os.stat(name).st_blocks, 0)
    finally:
      os.remove(name)

  def testCreateDirectoriesAndFile(self):
    dir = tempfile.mkdtemp()

    name = os.path.join(dir, 'foo/file')
    size = 1024 ** 2
    base.createSparseFile(name, size)

    try:
      self.assertEqual(os.stat(name).st_size, size)
      self.assertEqual(os.stat(name).st_blocks, 0)
    finally:
      shutil.rmtree(dir)


class TestFindDistribution(mox.MoxTestBase):
  def test(self):
    entry_point = self.mox.CreateMock(pkg_resources.EntryPoint)

    self.mox.StubOutWithMock(pkg_resources, 'iter_entry_points')
    pkg_resources.iter_entry_points(
      'debmarshal.distributions',
      name='base').AndReturn(
      (x for x in [entry_point]))

    entry_point.load().AndReturn(object)

    self.mox.ReplayAll()

    self.assertEqual(base.findDistribution('base'), object)


if __name__ == '__main__':
  unittest.main()
