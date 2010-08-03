#!/usr/bin/perl -w
#
# Test pooldebclean.pl's parse_packages()
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

my $pooldebclean = './pooldebclean.pl';

require_ok($pooldebclean);


my $packages = new IO::String <<EOF;
Package: package
Priority: optional
Section: utils
Installed-Size: 1
Maintainer: Someone <someone\@debian.org>
Architecture: all
Version: 0.5-3
Filename: pool/main/p/package/package_0.5-3_all.deb
Size: 243
MD5sum: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
SHA1: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
SHA256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Description: A sample tool
 A tool that does very little
Tag: implemented-in::perl, role::program, use::converting

EOF

my (%packages);
parse_packages($packages,\%packages);
is_deeply(\%packages, { 'pool/main/p/package/package_0.5-3_all.deb' => 1 },
	 "Package filename parsed");
