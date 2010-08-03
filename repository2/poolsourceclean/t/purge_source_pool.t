#!/usr/bin/perl -w
#
# Test poolsourceclean.pl's purge_source_pool()
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

my $tempdir =  tempdir( CLEANUP => 1);

my (%sources,%removed);
sub count_remove {
  my ($filename) = @_;
  $removed{$filename}++;
}

mkdir("$tempdir/pool");
mkdir("$tempdir/pool/t");
system("touch","$tempdir/pool/t/test_1.dsc");
system("touch","$tempdir/pool/t/test_2.dsc");
system("touch","$tempdir/pool/t/test_2.deb");
system("mkfifo","$tempdir/pool/fifo");
$sources{"pool/t/test_2.dsc"} = 1;
purge_source_pool("$tempdir/pool","pool",\%sources,\&count_remove);
is_deeply(\%removed, { "$tempdir/pool/t/test_1.dsc" => 1}, "purged pool");

