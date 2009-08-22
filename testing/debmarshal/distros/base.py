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
import subprocess

import pkg_resources

from debmarshal import errors


def captureCall(popen_args, stdin_str=None, *args, **kwargs):
  """Capture stdout from a command.

  This method will proxy the arguments to subprocess.Popen. It returns
  the output from the command if the call succeeded and raises an
  exception if the process returns a non-0 value.

  This is intended to be a variant on the subprocess.check_call
  function that also allows you access to the output from the command.

  Args:
    popen_args: A string or sequence of program arguments. (The first
      argument to subprocess.Popen)
    stdin_str: A string to pass in on stdin. This requires the stdin
      kwarg to either be unset or subprocess.PIPE.
    All other arguments are the same as the arguments to subprocess.Popen

  Returns:
    Anything printed on stdout by the process.

  Raises:
    debmarshal.errors.CalledProcessError: Raised if the command
      returns non-0.
  """
  if 'stdin' not in kwargs:
    kwargs['stdin'] = subprocess.PIPE
  if 'stdout' not in kwargs:
    kwargs['stdout'] = subprocess.PIPE
  if 'stderr' not in kwargs:
    kwargs['stderr'] = subprocess.STDOUT
  p = subprocess.Popen(popen_args, *args, **kwargs)
  out, _ = p.communicate(stdin_str)
  if p.returncode:
    raise errors.CalledProcessError(p.returncode, popen_args, out)
  return out


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
