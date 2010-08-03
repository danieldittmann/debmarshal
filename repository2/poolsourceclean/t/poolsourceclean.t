#!/usr/bin/perl -w
#
# Test pooldebclean.pl's poolsourceclean()
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

my $poolsourceclean = './poolsourceclean.pl';

require_ok($poolsourceclean);

my $tempdir =  tempdir( CLEANUP => 1);

is_deeply(poolsourceclean("$tempdir/missing"),
	  ["$tempdir/missing/ does not exist", 2],
	  "missing repository");

is_deeply(poolsourceclean($tempdir),
	  ["$tempdir/dists/ does not exist", 2],
	  "missing dists");

mkdir "$tempdir/dists";
is_deeply(poolsourceclean($tempdir),
	  ["$tempdir/pool/ does not exist", 2],
	  "missing pool");

mkdir "$tempdir/pool";
is_deeply(poolsourceclean($tempdir),
	  [undef, 0],
	  "poolsourceclean repository prereqs OK");

open(SOURCES,">","$tempdir/dists/Sources");
print SOURCES <<EOF;
Directory: pool/t
Files:
 aa 0 test_2.dsc

EOF
close(SOURCES);
mkdir "$tempdir/pool/t";
system("touch","$tempdir/pool/t/test_1.dsc");
system("touch","$tempdir/pool/t/test_2.dsc");
is_deeply(poolsourceclean($tempdir),
	  [undef, 0],
	  "poolsourceclean parsed Sources");
ok(! -f "$tempdir/pool/t/test_1.dsc", "unreferenced source deleted");
ok(-f "$tempdir/pool/t/test_2.dsc", "referenced source saved");
