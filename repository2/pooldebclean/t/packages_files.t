#!/usr/bin/perl -w
#
# Test pooldebclean.pl's packages_files()
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
use Test::More tests => 3;
use File::Temp qw/ tempdir/;
use IO::String;
use File::Path qw(make_path remove_tree);;

my $pooldebclean = './pooldebclean.pl';

require_ok($pooldebclean);

my $tempdir =  tempdir( CLEANUP => 1);

is(packages_files($tempdir), 0, "no Packages files");

make_path "$tempdir/sid/98/main/binary-amd64/";
make_path "$tempdir/sid/98/main/binary-i386/";
make_path "$tempdir/sid/99/main/binary-amd64/";
make_path "$tempdir/sid/99/main/binary-i386/";
symlink("98","$tempdir/sid/stable");
symlink("98","$tempdir/sid/latest");
symlink("broken","$tempdir/sid/broken.link");
system("touch","$tempdir/README");
system("touch","$tempdir/sid/98/main/binary-amd64/Packages");
system("touch","$tempdir/sid/98/main/binary-i386/Packages");
system("touch","$tempdir/sid/99/main/binary-amd64/Packages");
system("touch","$tempdir/sid/99/main/binary-i386/Packages");

my @packages = packages_files($tempdir);
sort @packages;

is_deeply(\@packages,
	  [ "$tempdir/sid/98/main/binary-amd64/Packages",
	    "$tempdir/sid/98/main/binary-i386/Packages",
	    "$tempdir/sid/99/main/binary-amd64/Packages",
	    "$tempdir/sid/99/main/binary-i386/Packages"
	  ],
	"Packages file");
