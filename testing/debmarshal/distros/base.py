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
"""Base for debmarshal's distribution representation classes."""


__authors__ = [
    'Evan Broder <ebroder@google.com>',
]


import os

import pkg_resources


def createSparseFile(path, len):
  """Create a sparse file.

  Create a sparse file with a given length, say for use as a disk
  image.

  It is the caller's responsibility to ensure that the passed in path
  doesn't exist, or can be overwritten.

  Args:
    path: Path to the file to be created.
    len: Length of the sparse file in bytes.
  """
  dir = os.path.dirname(path)
  if not os.path.exists(dir):
    os.makedirs(dir)
  open(path, 'w').truncate(len)


def findDistribution(name):
  """Find an installed distribtion.

  Args:
    name: The name of the distribution to use. This should be the name
      of an entry_point providing debmarshal.distributions

  Returns:
    The class providing the entry_point of the given name.
  """
  entry_points = list(pkg_resources.iter_entry_points(
      'debmarshal.distributions',
      name=name))
  assert len(entry_points) == 1

  return entry_points.pop().load()
