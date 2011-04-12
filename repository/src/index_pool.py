#!/usr/bin/python
#
# Copyright 2006 Google Inc.
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

"""Script to index package files in the pool hierarchy

The index_pool.py script is a repository-administrator command that
traverses through the pool/ hierarchy and indexes all package files it
finds there.  The script skips over files that have already been
indexed, so the indexing operation is practically idempotent.
"""

__author__ = 'cklin@google.com (Chuan-Kai Lin)'

import logging as lg
import os
import sys
import bsddb_utils as bu
import deb_utils as du
import logging_utils as lu
import os_utils as ou
import package_utils as pu
import release_utils as ru
import setting_utils as su
import optparse

_new_package = False
retry_packages = []


def IndexPool((src_names, pkg_names), dbs):
  """Index the specified source and binary packages

  This function accepts lists of source and binary package pathnames
  as input and indexes those package files into the database.  This
  step is necessary for debmarshal to consider a package for release.
  Note that the package files should be at their final location; once
  indexed, they should never again be moved.
  """

  def CountProgress():
    """Count the number of items to be processed
    """

    global source_count, binary_count, source_progress, binary_progress
    source_count = 0
    binary_count = 0
    source_progress = 0
    binary_progress = 0

    if 'options' in globals() and options.progress:
      for name in src_names:
        src = os.path.split(name)[1]
        if not src in pool_pkg:
          source_count += 1
      for name in pkg_names:
        pkg = os.path.split(name)[1]
        if pkg in retry_packages or pkg not in pool_pkg:
          binary_count += 1
      lg.info('Found ' + str(source_count) + ' source packages and '
              + str(binary_count) + ' binary packages to index')

  def DisplayProgress(type, text, count, progress):
    """Display progress information and the specified text if progress
    is enabled. If not, just display the specified text.
    """
    if count == 0 or not options.progress:
      lg.info(text)
      return

    percent = int((progress * 100) / count)
    lg.info('[' + type + ' ' + str(percent) + '%] ' + text)

  def IndexSource(name):
    """Index a source package (pool_pkg, src_info)
    """

    global _new_package, source_count, source_progress

    src = os.path.split(name)[1]
    if src in pool_pkg:
      file_size = str(os.stat(name).st_size)
      if pool_pkg[src] != file_size:
        lg.warning('File ' + name + ' does not match indexed data')
      return

    DisplayProgress('Sources', 'Indexing ' + name, source_count, source_progress)
    pool_pkg[src] = str(os.stat(name).st_size)
    lines = ou.RunWithFileInput(pu.StripSignature, name)
    attr_dict = pu.ParseAttributes(lines)
    nv = pu.GetSourceID(attr_dict)
    src_info[nv] = du.BuildSrcInfoText(name, attr_dict)
    _new_package = True
    source_progress += 1

  def IndexBinary(name):
    """Index a binary package (pool_pkg, pkg_info, pkg_deps, file_pkg)
    """

    global _new_package, binary_count, binary_progress

    pkg = os.path.split(name)[1]
    if pkg in pool_pkg:
      file_size = str(os.stat(name).st_size)
      if pool_pkg[pkg] != file_size:
        lg.warning('File ' + name + ' does not match indexed data')
      if pkg in retry_packages:
        lg.info('Re-indexing package '+pkg)
      else:
        return

    DisplayProgress('Binaries', 'Indexing ' + name, binary_count, binary_progress)
    pool_pkg[pkg] = str(os.stat(name).st_size)
    binary_progress += 1

    try:
      contents, attr_dict = du.ParseDebInfo(os.path.abspath(name))
    except IOError:
      lg.warning('File ' + name + ' threw an IOError while parsing.  ' +
                 'Discarding bad .deb')
      return

    nva = pu.GetPackageID(attr_dict)
    pkg_info[nva] = du.BuildDebInfoText(name, attr_dict)
    pkg_deps[nva] = du.BuildDependencyString(name, attr_dict)
    _new_package = True

    # We do not enter the debian-installer packages into file_pkg
    # because these packages are never installed on a normal system.

    if not name.endswith('.udeb'):
      for f in contents:
        bu.AppendEntry(file_pkg, f, nva)

  pkg_info = dbs['pkg_info']
  src_info = dbs['src_info']
  pkg_deps = dbs['pkg_deps']
  file_pkg = dbs['file_pkg']
  pool_pkg = dbs['pool_pkg']

  CountProgress()
  for name in src_names:
    IndexSource(name)
  for name in pkg_names:
    IndexBinary(name)
  return ru.SelectLatestPackages(pkg_info)


def _TraversePool():
  """Compile lists of package files in the pool hierarchy
  """

  def DoTraverse(_arg, dir, names):
    for name in names:
      if name.endswith('.dsc'):
        src_names.append(os.path.join(dir, name))
      elif name.endswith('.deb') or name.endswith('.udeb'):
        pkg_names.append(os.path.join(dir, name))

  src_names = []
  pkg_names = []
  os.path.walk('pool', DoTraverse, None)
  return src_names, pkg_names

def _ParseCommandLine():
  """Parse and check command line options and arguments

  This function uses the optparse module to parse the command line
  options, and it then checks that the command line arguments are
  well-formed in accordance with the semantics of the script.
  """

  usage = 'usage: %prog [options] [repos-directory]'
  version = 'Debmarshall 0.0'
  parser = optparse.OptionParser(usage=usage, version=version)
  parser.add_option('-r', '--retry',
                    dest='retry', metavar='FILE', action='append',
                    help='read package names to re-index from FILE')
  parser.add_option('-p', '--progress',
                    dest='progress', action='store_true',
                    help='display progress information')

  options, proper = parser.parse_args()
  return options, proper

def main(options, repo_dir):
  global _new_package
  global retry_packages

  def DoImport(lines):
    p = []
    for line in lines:
      p.append(line.rstrip('\n'))
    return p

  # If --retry option was specified, import lists of packages to be retried
  if options.retry is not None:
    for retry in options.retry:
      retry_packages.extend(ou.RunWithFileInput(DoImport, retry))

  current_cwd = os.getcwd()
  lu.SetLogConsole()
  try:
    os.chdir(repo_dir)
    if su.GetSetting(None, 'Mode') != 'tracking':
      lg.error('Repository is not in tracking mode')
      sys.exit()
    try:
      names = _TraversePool()
      packages = bu.RunWithDB(None, IndexPool, names)
      if _new_package:
        ru.GenerateReleaseList('snapshot', packages)
    except KeyboardInterrupt:
      lg.info('Received keyboard interrupt, terminating...')
  finally:
    os.chdir(current_cwd)


if __name__ == '__main__':
  options, proper = _ParseCommandLine()
  if len(proper) == 1:
    main(options, proper[0])
  else:
    main(options, os.getcwd())



