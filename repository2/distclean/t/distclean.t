#!/usr/bin/perl -w
#
# Test distclean.pl's distclean()
#
#
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Drake Diedrich <dld@google.com>

use strict;
use Test::More tests => 8;
use File::Temp qw/ tempdir/;

my $distclean = './distclean.pl';

require_ok($distclean);

my $tempdir =  tempdir( CLEANUP => 1);

is_deeply(distclean("$tempdir/missing","null",[]),
	  ["$tempdir/missing/ does not exist", 2],
	  "missing repository");

is_deeply(distclean($tempdir,"null",[]),
	  ["$tempdir/dists/ does not exist", 2],
	  "empty repository");

mkdir "$tempdir/dists";
is_deeply(distclean($tempdir,"stable",[]),
	  ["$tempdir/dists/stable/ does not exist", 2],
	  "missing dist");

mkdir "$tempdir/dists/stable";
is_deeply(distclean($tempdir,"stable",[]),
	  [undef, 0],
	  "subdirectory of dist snapshots found");

mkdir "$tempdir/dists/stable/0";
mkdir "$tempdir/dists/stable/1";
symlink 1, "$tempdir/dists/stable/latest";
is_deeply(distclean($tempdir,"stable",[]),
	  [undef, 0],
	  "subdirectory of dist snapshots found");
ok(-d "$tempdir/dists/stable/1", " snapshot 1 kept");
ok(! -d "$tempdir/dists/stable/0", " snapshot 0 purge");
