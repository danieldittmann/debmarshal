#!/usr/bin/perl -w
#
# Test pooldebclean.pl's pooldebclean()
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

my $pooldebclean = './pooldebclean.pl';

require_ok($pooldebclean);

my $tempdir =  tempdir( CLEANUP => 1);

is_deeply(pooldebclean("$tempdir/missing"),
	  ["$tempdir/missing/ does not exist", 2],
	  "missing repository");

is_deeply(pooldebclean($tempdir),
	  ["$tempdir/dists/ does not exist", 2],
	  "missing dists");

mkdir "$tempdir/dists";
is_deeply(pooldebclean($tempdir),
	  ["$tempdir/pool/ does not exist", 2],
	  "missing pool");

mkdir "$tempdir/pool";
is_deeply(pooldebclean($tempdir),
	  [undef, 0],
	  "pooldebclean repository prereqs OK");

open(PACKAGES,">","$tempdir/dists/Packages");
print PACKAGES "Filename: pool/test.deb\n";
close(PACKAGES);
system("touch","$tempdir/pool/test.deb");
system("touch","$tempdir/pool/test2.deb");
is_deeply(pooldebclean($tempdir),
	  [undef, 0],
	  "pooldebclean parsed Packages");
ok(-f "$tempdir/pool/test.deb", "referenced deb saved");
ok(! -f "$tempdir/pool/test2.deb", "unreferenced deb deleted");
