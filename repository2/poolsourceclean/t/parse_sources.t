#!/usr/bin/perl -w
#
# Test pooldebclean.pl's parse_sources()
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
use Test::More tests => 2;
use File::Temp qw/ tempdir/;
use IO::String;

my $poolsourceclean = './poolsourceclean.pl';

require_ok($poolsourceclean);


my $sources = new IO::String <<EOF;
Package: test
Binary: test-bin
Version: 1
Directory: pool/main/t/test
Files:
 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 0 test_1.dsc

EOF

my (%sources);
parse_sources($sources,\%sources);
is_deeply(\%sources, { 'pool/main/t/test/test_1.dsc' => 1 },
	 "Source filename parsed");
