#!/usr/bin/perl -w
#
# Test pooldebclean.pl's main()
#
# Doesn't produce coverage reports, but it is exercising the code
# through a subprocess.  This is required as the standard perl option
# and pod parsers can exit.
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
use Test::More tests => 4;

my $pooldebclean = './pooldebclean.pl';

require_ok($pooldebclean);

is(system($pooldebclean), 2<<8, "zero args");
is(system($pooldebclean,"--badoption"), 2<<8, "--badoption");
is(system($pooldebclean,"--help"), 1<<8, "--help");
